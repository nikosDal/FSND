# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 

## Tasks

One note before you delve into your tasks: for each endpoint you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior. 

1. Use Flask-CORS to enable cross-domain requests and set response headers. 
2. Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories. 
3. Create an endpoint to handle GET requests for all available categories. 
4. Create an endpoint to DELETE question using a question ID. 
5. Create an endpoint to POST a new question, which will require the question and answer text, category, and difficulty score. 
6. Create a POST endpoint to get questions based on category. 
7. Create a POST endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question. 
8. Create a POST endpoint to get questions to play the quiz. This endpoint should take category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions. 
9. Create error handlers for all expected errors including 400, 404, 422 and 500. 

## API documentation

### Endpoints
```
GET '/categories'
GET '/questions'
POST '/questions'
DELETE '/questions/<question_id>'
POST '/questions/search'
GET '/categories/<category_id>/questions'
POST '/quizzes'
```

#### `GET '/categories'`
- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns: An object with a single key, categories, that contains a object of id: category_string key:value pairs. 
```
{'1' : "Science",
'2' : "Art",
'3' : "Geography",
'4' : "History",
'5' : "Entertainment",
'6' : "Sports"}
```
- If no categories found, returns HTTP 404

#### `GET '/questions'`
- Fetches questions in pages of 10, with default page number 1, order by question id
- Request Arguments: page (int)
- Returns: JSON with following schema:
```
    {
        success: boolean,
        questions: [ {
            answer: string,
            category: int,
            difficulty: int,
            id: int,
            question: string
        } ],
        current_category: int,
        total_questions: int
    }
```

#### `POST '/questions'`
- Inserts new question to the database
- Request Arguments: JSON with schema
```
    {
        question: str,
        answer: str,
        difficulty: int between 1 and 5,
        category: int matching a category id
    }
```
- Returns: JSON {success: True}
- If any of the parameters are missing, returns HTTP 422
- If any of the parameters are invalid, returns HTTP 400

#### `DELETE '/questions/<question_id>'`
- Deletes the question with the given id from the datbase
- Request Arguments: question_id (int)
- Returns: JSON {success: True}
- If question_id is missing, returns HTTP 404

#### `POST '/questions/search'`
- Looks for and returns questions matching the given search term. If blank searchTerm is given, all questions are returned
  paginated (same as GET '/questions'). Otherwise, all search results are shown without pagination. If no questions match,
  an empty list is returned.
- Request Arguments: JSON {searchTerm: str}
- Returns: JSON with schema
``` 
    {
        success: boolean,
        questions: [{
            question: str,
            answer: str,
            difficulty: int,
            category: int
        }],
        total_questions: int (total number of questions matching),
        curent_category: int
    }
```
- If searchTerm is missing, returns HTTP 422

#### `GET '/categories/<category_id>/questions'`
- Returns list of questions for the given category
- Request Arguments: category_id (int)
- Returns: JSON as per GET '/questions'
- If no questions found, returns HTTP 404

#### `POST '/quizzes'`
- Takes in a list of question ids and a category id (with 0 representing ALL) and returns
  a random question from that category (or across categories) that is not in the list of
  questions given. If there are no available questions, it returns null.
- Request Arguments: JSON with schema
```
    {
        quiz_category: { id: int, type: string },
        previous_questions: [ id: int ]
    }
```
- Returns: JSON with schema
```
    {
        success: boolean,
        question: {
            question: string,
            answer: string,
            id: int,
            difficulty: int,
            category: int
        }
    }
```
- If either the quiz_category or previous_questions are missing from the request, returns HTTP 422


## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```