class QuizValidation:
    """
    Server-side validation of quiz data.
    Every method returns None if everything is OK, otherwise a text describing the error.
    """

    TITLE_MIN = 3
    TITLE_MAX = 100
    DURATION_MIN = 10        # seconds
    DURATION_MAX = 3600      # seconds
    QUESTIONS_MAX = 50
    OPTIONS_MIN = 2
    OPTIONS_MAX = 10
    POINTS_MIN = 1
    POINTS_MAX = 100

    @staticmethod
    def _is_int(value) -> bool:
        return isinstance(value, int) and not isinstance(value, bool)

    @staticmethod
    def _is_text(value) -> bool:
        return isinstance(value, str) and value.strip() != ""

    @staticmethod
    def validate_quiz(data):
        """CREATE / EDIT QUIZ"""
        if not isinstance(data, dict):
            return "Request body must be JSON"

        # TITLE
        title = data.get("title")
        if not QuizValidation._is_text(title):
            return "Quiz title is required"
        if not (QuizValidation.TITLE_MIN <= len(title.strip()) <= QuizValidation.TITLE_MAX):
            return f"Quiz title must have {QuizValidation.TITLE_MIN}-{QuizValidation.TITLE_MAX} characters"

        # DURATION
        duration = data.get("duration")
        if not QuizValidation._is_int(duration):
            return "Duration must be a whole number of seconds"
        if not (QuizValidation.DURATION_MIN <= duration <= QuizValidation.DURATION_MAX):
            return f"Duration must be between {QuizValidation.DURATION_MIN} and {QuizValidation.DURATION_MAX} seconds"

        # QUESTIONS
        questions = data.get("questions")
        if not isinstance(questions, list) or len(questions) == 0:
            return "Quiz must have at least one question"
        if len(questions) > QuizValidation.QUESTIONS_MAX:
            return f"Quiz can have at most {QuizValidation.QUESTIONS_MAX} questions"

        for number, question in enumerate(questions, start=1):
            error = QuizValidation._validate_question(question)
            if error:
                return f"Question {number}: {error}"

        # AUTHOR
        if not QuizValidation._is_text(data.get("author_name")):
            return "Author name is missing"

        return None

    @staticmethod
    def _validate_question(question):
        if not isinstance(question, dict):
            return "invalid format"

        if not QuizValidation._is_text(question.get("text")):
            return "text is required"

        points = question.get("points")
        if not QuizValidation._is_int(points) or not (QuizValidation.POINTS_MIN <= points <= QuizValidation.POINTS_MAX):
            return f"points must be a whole number between {QuizValidation.POINTS_MIN} and {QuizValidation.POINTS_MAX}"

        options = question.get("options")
        if not isinstance(options, list):
            return "options are required"
        if not (QuizValidation.OPTIONS_MIN <= len(options) <= QuizValidation.OPTIONS_MAX):
            return f"must have between {QuizValidation.OPTIONS_MIN} and {QuizValidation.OPTIONS_MAX} options"
        if not all(QuizValidation._is_text(o) for o in options):
            return "options cannot be empty"

        clean_options = [o.strip() for o in options]
        if len(set(clean_options)) != len(clean_options):
            return "options must be different from each other"

        correct = question.get("correct_answers")
        if not isinstance(correct, list) or len(correct) == 0:
            return "at least one correct answer must be selected"
        for answer in correct:
            if not isinstance(answer, str) or answer.strip() not in clean_options:
                return "every correct answer must be one of the options"

        return None

    @staticmethod
    def validate_review(data):
        """ADMIN APPROVES / REJECTS"""
        if not isinstance(data, dict):
            return "Request body must be JSON"

        status = data.get("status")
        if status not in ("APPROVED", "REJECTED"):
            return "Status must be APPROVED or REJECTED"

        if status == "REJECTED" and not QuizValidation._is_text(data.get("rejection_reason")):
            return "Rejection reason is required when rejecting a quiz"

        return None

    @staticmethod
    def validate_submission(data):
        """PLAYER SENDS ANSWERS"""
        if not isinstance(data, dict):
            return "Request body must be JSON"

        answers = data.get("answers")
        if not isinstance(answers, list):
            return "Answers must be a list"
        for answer in answers:
            if not isinstance(answer, dict):
                return "Invalid answer format"
            if not QuizValidation._is_int(answer.get("question_index")):
                return "Every answer needs a question_index"
            selected = answer.get("selected")
            if not isinstance(selected, list) or not all(isinstance(s, str) for s in selected):
                return "Selected options must be a list of texts"

        time_spent = data.get("time_spent")
        if not QuizValidation._is_int(time_spent) or time_spent < 0:
            return "Time spent must be a positive whole number"

        if not QuizValidation._is_text(data.get("user_name")):
            return "Player name is missing"

        return None
