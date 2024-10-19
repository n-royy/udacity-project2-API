import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category, db

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.app.config['TESTING'] = True

        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            # Define mock data
            Category(type="Science").insert()
            Category(type="Art").insert()
            Question(question="Who discovered penicillin?", answer='Alexander Fleming', category=1, difficulty=1).insert()
            Question(question='Hematology is a branch of medicine involving the study of what?', answer='Blood', category=2, difficulty=4).insert()

    def tearDown(self):
        # Drop all tables after each test
        with self.app.app_context():
            db.session.remove()  # Remove the session
            db.drop_all()  # Drop all tables
        pass

    """
    DONE
    Write at least one test for each test for successful operation and for expected errors.
    """
    # GET /invalidurl
    def test_get_notfound_url(self):
        response = self.client.get("/invalidurl")
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "Not Found")

    # GET /categories
    def test_get_categories(self):
        response = self.client.get("/categories")
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["categories"], {
            "1": "Science",
            "2": "Art",
        })

    def test_get_questions(self):
        response = self.client.get('/questions')
        data = json.loads(response.data)
        # Assert the response
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["questions"],
            [
                {'answer': 'Alexander Fleming', 'category': '1', 'difficulty': 1, 'id': 1, 'question': "Who discovered penicillin?"}, 
                {'answer': 'Blood', 'category': '2', 'difficulty': 4, 'id': 2, 'question': 'Hematology is a branch of medicine involving the study of what?'}
            ]
        )

    def test_get_questions_by_page(self):
        response = self.client.get("/questions?page=2")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["questions"], [])
        self.assertEqual(data["categories"], {
            '1': 'Science', '2': 'Art'
        })

    def test_create_and_delete_question(self):
        # POST /questions  
        createResponse = self.client.post("/questions", json={
            "question": "Test question",
            "answer": "Test answer",
            "difficulty": 1,
            "category": 1
        })
        createData = json.loads(createResponse.data)

        self.assertEqual(createResponse.status_code, 200)
        self.assertTrue(createData["success"])
        self.assertEqual(createData["message"], "Question created successfully")

        # DELETE /questions/<int:question_id>
        deleteResponse = self.client.delete("/questions/1")
        deleteData = json.loads(deleteResponse.data)

        self.assertEqual(deleteResponse.status_code, 200)
        self.assertTrue(deleteData["success"])
        self.assertEqual(deleteData["message"], "Question deleted successfully")

    def test_delete_question_fail(self):
        response = self.client.delete("/questions/999")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "Unprocessable Entity")
    
    def test_post_question_fail(self):
        response = self.client.post("/questions", json={
            "question": "Test question",
            "answer": None,
            "difficulty": 1,
            "category": 1
        })

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "Unprocessable Entity")

    # POST /questions/search
    def test_search_questions(self):
        response = self.client.post("/questions/search", json={
            "searchTerm": "Hematology"
        })

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["questions"],
            [
                {'answer': 'Blood', 'category': '2', 'difficulty': 4, 'id': 2, 'question': 'Hematology is a branch of medicine involving the study of what?'}
            ]
        )
        self.assertEqual(data["total_questions"], 1)
    
    def test_search_questions_not_found(self):
        response = self.client.post("/questions/search", json={
            "searchTerm": "complex text"
        })

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["questions"], [])
        self.assertEqual(data["total_questions"], 0)

    # GET /categories/<int:category_id>/questions
    def test_get_questions_by_category(self):
        response = self.client.get("/categories/1/questions")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["questions"],
            [
                {'answer': 'Alexander Fleming', 'category': '1', 'difficulty': 1, 'id': 1, 'question': "Who discovered penicillin?"}, 
            ]
        )
        self.assertEqual(data["total_questions"], 1)

    def test_get_questions_by_category_not_found(self):
        response = self.client.get("/categories/10/questions")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["questions"], [])
        self.assertEqual(data["total_questions"], 0)
        self.assertEqual(data["current_category"], 0)

    # POST /quizzes
    def test_get_quiz_question(self):
        response = self.client.post("/quizzes", json={
            "previous_questions": [],
            "quiz_category": {
                "id": 0,
                "type": "All"
            }
        })
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["question"])

    def test_get_quiz_question_fail(self):
        response = self.client.post("/quizzes", json={
            "previous_questions": [1],
            "quiz_category": {
                "id": 1,
                "type": "All"
            }
        })

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertNotIn("question", data)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
