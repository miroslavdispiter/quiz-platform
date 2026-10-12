from flask import Blueprint, request, jsonify
from Database.database import db_mongo
from Domain.DTOs.dtos import QuizDTO, QuestionDTO
from datetime import datetime
import requests
import os
from bson import ObjectId
import time
from multiprocessing import Process
from Extensions.EmailSender import EmailSender
import json
import redis
from redis.retry import Retry
from redis.backoff import NoBackoff


quiz_db = Blueprint("quiz_db", __name__)
collection = db_mongo.get_collection("quizzes")
email_sender = EmailSender()

# Redis je opcion: ako REDIS_HOST nije postavljen, kes se preskace i sve ide direktno iz MongoDB-a
REDIS_HOST = os.getenv("REDIS_HOST")
redis_client = redis.Redis(
    host=REDIS_HOST, port=int(os.getenv("REDIS_PORT", 6379)), db=0, decode_responses=True,
    socket_connect_timeout=1, socket_timeout=1,
    retry=Retry(NoBackoff(), 0),  # bez ponovnih pokusaja: ako Redis ne radi, odmah idemo na MongoDB
) if REDIS_HOST else None

# AUXILIARY FUNCTION FOR CLEARING THE CACHE
def clear_quiz_cache():
    if redis_client is None:
        return
    try:
        redis_client.delete("published_quizzes")
    except Exception as e:
        print(f"Redis error: {e}")

# CREATE QUIZ
@quiz_db.route("/", methods=["POST"])
def create_quiz():
    data = request.get_json(silent=True) or {}

    questions = []
    for q in data.get("questions", []):
        text = q.get("text") or q.get("question") or ""

        if "correct_answers" in q:
            correct_answers = q.get("correct_answers") or []
        else:
            ans = q.get("answer")
            correct_answers = [str(ans)] if ans is not None else []

        points = q.get("points", 1)

        questions.append(
            QuestionDTO(
                text=text,
                options=q.get("options", []),
                correct_answers=correct_answers,
                points=points,
            )
        )

    title = data.get("title") or data.get("name") or "Untitled quiz"
    author_id = data.get("author_id") or data.get("authorId") or 0
    duration = data.get("duration") or data.get("time_limit") or 60

    new_quiz = QuizDTO(
        title=title,
        author_id=author_id,
        duration=duration,
        questions=questions,
    )

    quiz_dict = new_quiz.to_disc()
    quiz_dict.setdefault("status", "PENDING")
    quiz_dict.setdefault("created_at", datetime.utcnow().isoformat() + "Z")

    result = collection.insert_one(quiz_dict)

    try:
        main_server_url = os.getenv("MAIN_SERVER_URL")
        requests.post(
            f"{main_server_url}/api/quizzes/notify-admin",
            json={"quiz_id": str(result.inserted_id), "title": new_quiz.title},
            timeout=5,
        )
    except Exception as e:
        print(f"Greska pri slanju obavjestenja serveru: {e}")

    return jsonify({"message": "Quiz created and pending approval", "id": str(result.inserted_id)}), 201

# QUIZ STATUS CHANGE
@quiz_db.route("/<quiz_id>/status", methods=["PATCH"])
def update_quiz_status(quiz_id):
    data = request.json
    new_status = data.get("status") # Approved or Rejected
    reason = data.get("rejection_reason", "")

    update_data = {"status": new_status}
    if new_status == "REJECTED":
        update_data["rejection_reason"] = reason

    result = collection.update_one(
        {"_id": ObjectId(quiz_id)},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        return jsonify({"message": "Quiz not found"}), 404
    
    clear_quiz_cache() # We delete the cache because the status has changed
    
    return jsonify({"message": f"Quiz status updated to {new_status}"}), 200

# LISTING ALL QUIZZES
@quiz_db.route("/", methods=["GET"])
def get_quizzes():
    quizzes = list(collection.find())
    for q in quizzes:
        q['_id'] = str(q['_id'])
    return jsonify(quizzes), 200

# LISTING ONLY APPROVED QUIZZES
@quiz_db.route("/published", methods=["GET"])
def get_published_quizzes():
    #prvo probamo iz kesa
    if redis_client is not None:
        try:
            cached_quizzes = redis_client.get("published_quizzes")
            if cached_quizzes:
                print("CACHE HIT: redis data")
                return jsonify(json.loads(cached_quizzes)), 200
        except Exception as e:
            print(f"Redis error (hit): {e}")

    # If it's not in the cache, we take it from MognoDB
    print("CACHE MISS: MongoDB data")
    quizzes = list(collection.find({"status": "APPROVED"}))

    for q in quizzes:
        q['_id'] = str(q['_id'])
        for question in q.get('questions', []):
            question.pop("correct_answers", None)
            
    # Save the result to redis every 5min
    if redis_client is not None:
        try:
            redis_client.setex("published_quizzes", 300, json.dumps(quizzes))
        except Exception as e:
            print(f"Redis error (set): {e}")
        
    return jsonify(quizzes), 200

# Initiating the process
def process_quick_task(quiz_data, user_answers, user_email, time_spent):
    print(f"Asynchronous processing started for {user_email}...")
    time.sleep(10)  

    correct_count = 0
    total_points = sum(int(q.get('points', 0)) for q in quiz_data['questions'])
    achieved_points = 0

    for idx, question in enumerate(quiz_data['questions']):
        user_ans = next((a for a in user_answers if a.get('question_index') == idx), None)

        if user_ans:
            u_selected = [str(x).strip() for x in user_ans.get('selected', [])]
            db_correct = [str(x).strip() for x in question.get('correct_answers', [])]

            if set(u_selected) == set(db_correct):
                achieved_points += int(question.get('points', 0))
                correct_count += 1

    percentage = (achieved_points / total_points * 100) if total_points > 0 else 0

    print(f"Finished calculating, achieved: {achieved_points} points. Sending to {user_email}")

    
    try:
        email_sender.send_quiz_result_email(
            to_email=user_email,
            quiz_title=quiz_data.get('title', 'Kviz'),
            score=achieved_points,
            total=len(quiz_data['questions']),
            percentage=round(percentage, 2)
        )
        print(f"Email successfully sent to {user_email}")

    except Exception as e:
        print(f"Error sending email in background process: {e}")

    
    try:
        main_server_url = os.getenv("MAIN_SERVER_URL")
        internal_token = os.getenv("INTERNAL_API_KEY")

        requests.post(
            f"{main_server_url}/api/quizzes/internal/results",
            json={
                "user_email": user_email,
                "quiz_id": str(quiz_data.get("_id")),
                "quiz_title": quiz_data.get("title", "Kviz"),
                "score": int(achieved_points),
                "total_questions": len(quiz_data.get("questions", [])),
                "percentage": round(percentage, 2),
                "time_spent": time_spent
            },
            headers={"X-Internal-Token": internal_token},
            timeout=5
        )

        print("Result saved to MySQL (main server).")

    except Exception as e:
        print(f"Error saving result to main server: {e}")
# SENDING ANSWERS AND CALCULATING POINTS
@quiz_db.route("/<quiz_id>/submit", methods=["POST"])
def submit_quiz(quiz_id):
    data = request.json
    user_answers = data.get('answers', [])
    user_email = data.get('user_email') 

    time_spent = data.get("time_spent")

    quiz = collection.find_one({"_id": ObjectId(quiz_id)})
    if not quiz:
        return jsonify({"message": "Quiz not fount"}), 404
    
    p = Process(
    target=process_quick_task,
    args=(quiz, user_answers, user_email, time_spent))
    p.start()

    return jsonify({
        "message": "Quiz processing is started asynchronously. The results will be sent to you by email.",
        "status": "processing"
    }), 202
    
# QUIZ DELETE
@quiz_db.route("/<quiz_id>", methods=["DELETE"])
def delete_quiz(quiz_id):
    data = request.get_json() or {}
    requester_role = data.get("requester_role")
    requester_id = data.get("requester_id")

    quiz = collection.find_one({"_id": ObjectId(quiz_id)})
    if not quiz:
        return jsonify({"message": "Quiz not found"}), 404

    if requester_role != "ADMIN" and str(quiz.get("author_id")) != str(requester_id):
        return jsonify({"message": "Forbidden"}), 403

    collection.delete_one({"_id": ObjectId(quiz_id)})

    # CACHE DELETE
    clear_quiz_cache()

    return jsonify({"status": "deleted"}), 200

# GETTING ONLY ONE QUIZ
@quiz_db.route("/<quiz_id>", methods=["GET"])
def get_quiz_by_id(quiz_id):
    try:
        quiz = collection.find_one({"_id": ObjectId(quiz_id)})
        if not quiz:
            return jsonify({"message": "Quiz not found"}), 404
        
        quiz['_id'] = str(quiz['_id'])
        
        # The player must not see the correct answers before submitting the quiz
        if 'questions' in quiz:
            for q in quiz['questions']:
                q.pop('correct_answers', None)
        
        return jsonify(quiz), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

