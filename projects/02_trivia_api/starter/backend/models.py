from sqlalchemy import Column, String, Integer
from flask_sqlalchemy import SQLAlchemy

database_name = "trivia"
database_path = "postgres://{}/{}".format('localhost:5432', database_name)

db = SQLAlchemy()


'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


class Question(db.Model):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    question = Column(String)
    answer = Column(String)
    category = Column(String)
    difficulty = Column(Integer)

    def __init__(self, question, answer, category, difficulty):
        self.question = str(question)
        if self.question == '':
            raise ValueError('empty question given')
        self.answer = str(answer)
        if self.answer == '':
            raise ValueError('empty answer given')
        self.difficulty = int(difficulty)
        if self.difficulty < 1 or self.difficulty > 5:
            raise ValueError('difficulty must be between 1 and 5')
        self.category = int(category)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'category': self.category,
            'difficulty': self.difficulty
        }

    @classmethod
    def get_max_id(cls):
        return cls.query.order_by(Question.id.desc())[0].id

    @classmethod
    def get_total_questions(cls):
        return len(cls.query.all())


class Category(db.Model):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    type = Column(String)

    def __init__(self, type):
        self.type = type

    def format(self):
        return {
            'id': self.id,
            'type': self.type
        }
