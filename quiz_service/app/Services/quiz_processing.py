import time
from app.config import Config
from app.Database.QuizRepository import QuizRepository
from app.Database.ResultRepository import ResultRepository
from app.Extensions.email_sender import EmailSender
from app.Extensions.cache import cache, leaderboard_key


def process_result(result_id: str):
    """
    Runs in a SEPARATE PROCESS (started from ResultService.submit_answers).
    1. waits a bit (simulates long processing)
    2. calculates the points
    3. saves the result to the database
    4. sends the result to the player's email
    """
    print(f"[process] Processing result {result_id} started...")
    time.sleep(Config.PROCESSING_DELAY_SECONDS)

    result_repo = ResultRepository()
    quiz_repo = QuizRepository()

    result = result_repo.get_by_id(result_id)
    if not result:
        print(f"[process] Result {result_id} no longer exists - skipping.")
        return

    quiz = quiz_repo.get_by_id(result["quiz_id"])
    if not quiz:
        print(f"[process] Quiz of result {result_id} was deleted - skipping.")
        return

    score, correct_count = calculate_score(quiz["questions"], result["answers"])
    result_repo.mark_done(result_id, score, correct_count)
    print(f"[process] Result {result_id}: {score}/{result['max_score']} points.")

    cache.delete(leaderboard_key(result["quiz_id"]))

    if result.get("user_email"):
        try:
            sent = EmailSender().send_quiz_result_email(
                to_email=result["user_email"],
                full_name=result["user_name"],
                quiz_title=quiz["title"],
                score=score,
                max_score=result["max_score"],
                time_spent=result["time_spent"],
            )
            if sent:
                print(f"[process] Result email sent to {result['user_email']}.")
        except Exception as e:
            print(f"[process] Error sending email: {e}")


def calculate_score(questions, answers):
    """
    A question brings its points only if the player selected EXACTLY all correct answers
    """
    selected_by_question = {a["question_index"]: a["selected"] for a in answers}

    score = 0
    correct_count = 0
    for index, question in enumerate(questions):
        selected = set(s.strip() for s in selected_by_question.get(index, []))
        if selected == set(question["correct_answers"]):
            score += question["points"]
            correct_count += 1

    return score, correct_count
