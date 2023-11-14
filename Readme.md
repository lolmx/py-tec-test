#### Just a technical test I had to do

<details>
    <summary>Building a user registration API</summary>

## Context
XXX handles user registrations. To do so, user creates an account and we send a code by email to verify the account.
As a core API developer, you are responsible for building this feature and expose it through API.
## Specifications
You have to manage a user registration and his activation. 
The API must support the following use cases:
* Create a user with an email and a password.
* Send an email to the user with a 4 digits code.
* Activate this account with the 4 digits code received. For this step, we consider a `BASIC AUTH` is enough to check if he is the right user.
* The user has only one minute to use this code. After that, an error should be raised.
Design and build this API. You are completely free to propose the architecture you want.
## What do we expect?
- Python language is required.
- We expect to have a level of code quality which could go to production.
- Using frameworks is allowed only for routing, dependency injection, event dispatcher, db connection. FastAPI could be used. Don't use magic (ORM for example)! We want to see **your** implementation.
- Use the DBMS you want (except SQLite).
- Consider the SMTP server as a third party service offering an HTTP API. You can mock the call, use a local SMTP server running in a container, or simply print the 4 digits in console. But do not forget in your implementation that **it is a third party serv**
</details>

# Setup
Make sure you have python >= 3.10 and pipenv
```
$ python --version
$ pipenv --version
```

Install the project with ``$ pipenv install --dev``.

# Database
I used a MySQL database for this project, you'll need to create your own.

You can execute ``database.sql`` in your favorite DB viewer. It will create an empty dev database and a test database with some fixtures.

Update your database info in ``.env`` and ``test.env`` files.

The password for fixture users is ``password``. 

# Run
Run the project by executing
``$ uvicorn app.main:app``

# Test
To run the tests, simply execute
``$ pytest``
