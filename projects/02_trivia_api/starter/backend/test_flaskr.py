import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question


HEADERS = {'Content-Type': 'application/json'}


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['categories'])

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])

    def test_get_bad_page_questions(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertFalse(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])

    def test_get_category_1_questions(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category']['id'], 1)

    def test_get_category_1000_questions(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    def test_insert_ok_question(self):
        new_question = {
            'question': 'Which is the capital of Greece?',
            'answer': 'Athens',
            'difficulty': 1,
            'category': 3
        }
        res = self.client().post('/questions', headers=HEADERS, data=json.dumps(new_question))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['new_question'])

    def test_insert_question_missing_parameter(self):
        new_question = {'question': 'What?', 'answer': 'Something'}
        res = self.client().post('/questions', headers=HEADERS, data=json.dumps(new_question))
        self.assertEqual(res.status_code, 422)

    def test_insert_question_bad_parameter(self):
        new_question = {'question': 'What?', 'answer': 'Something', 'difficulty': 10, 'category': 1}
        res = self.client().post('questions', headers=HEADERS, data=json.dumps(new_question))
        self.assertEqual(res.status_code, 400)

    def test_delete_existing_question(self):
        max_question_id = Question.get_max_id()
        res = self.client().delete(f'/questions/{max_question_id}')
        self.assertEqual(res.status_code, 200)

    def test_delete_nonexisting_question(self):
        res = self.client().delete('/questions/10000')
        self.assertEqual(res.status_code, 404)

    def test_question_search_with_results(self):
        search_term = {'searchTerm': 'a'}
        res = self.client().post('/questions/search', headers=HEADERS, data=json.dumps(search_term))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_question_search_with_no_results(self):
        search_term = {'searchTerm': 'zzzzzzzzzzzzzzzzzzz'}
        res = self.client().post('/questions/search', headers=HEADERS, data=json.dumps(search_term))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertFalse(data['questions'])
        self.assertEqual(data['total_questions'], 0)

    def test_quiz(self):
        quiz = {'quiz_category': {'id': 1}, 'previous_questions': []}
        res = self.client().post('/quizzes', headers=HEADERS, data=json.dumps(quiz))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])

    def test_bad_quiz(self):
        quiz = {'quiz_category': {'id': 1}}
        res = self.client().post('/quizzes', headers=HEADERS, data=json.dumps(quiz))
        self.assertEqual(res.status_code, 422)

    def test_0_category_quiz(self):
        quiz = {'quiz_category': {'id': 0}, 'previous_questions': []}
        res = self.client().post('/quizzes', headers=HEADERS, data=json.dumps(quiz))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])

    def test_quiz_with_no_answers_left(self):
        all_question_ids = [q.id for q in Question.query.all()]
        quiz = {'quiz_category': {'id': 0}, 'previous_questions': all_question_ids}
        res = self.client().post('/quizzes', headers=HEADERS, data=json.dumps(quiz))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertFalse(data['question'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
