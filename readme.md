** How to get Started for development

1. Create a python 3.6/3.7 venv
2. Install requirements using requirements-dev.txt
3. Start the virtual env
4. Run ```python manage.py makemigrations``` and ```python manage.py migrate``` to create database tables
4. start the dev server using ```python manage.py runserver```. Server will start on 127.0.0.1:8000 .


** How to run test locally

* We are using [Pytest](https://docs.pytest.org/en/latest/) for testing.
* Install test requirements - ```pip install -r requirements.txt```
* To check the test coverage - ```pytest core/tests ```


** How to access apis
register/ : register a user, takes in username and password
login/ : Login for a user , Takes in username and password created through the Register API , Returns a Token used for subsequent API access ex:  AUTHORIZATION: Token kbwefbsfksjbfgkbskbgsrgbk
get_transactions/ : Get all the transactions done by Logged in user
add_transaction/ : Add Transaction for a user , If user_id sent is empty takes the value for logged in user
mark_paid/ : Change transaction status to marked and unmarked
credit_score/ : Get the credit score for logged in user
