# Django OAuth2 and Simple JWT Integration for the Resource project, Client project just run separatly normally

This project demonstrates the integration of OAuth2 and Simple JWT for authentication in a Django application. It includes user registration, login, and API endpoint for generating and updating access tokens.

## Setup

1. Clone the repository:

    ```bash
    git clone https://github.com/niharMSQ1/OAuth2-practice2.git
    cd your-repository
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Create a virtual environment (optional but recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

4. Apply migrations:

    ```bash
    no need since the database is hosted on a cloud server
    ```

5. Create a superuser (for Django admin):

    ```bash
    I will share the username and password personally
    ```

6. Run the development server:

    ```bash
    python manage.py runserver
    ```

7. Visit [http://127.0.0.1:8001/admin/](http://127.0.0.1:8001/admin/) and log in with the superuser credentials.

## Endpoints

- **User Registration:** `/user/registration/` (POST)
- **User Login:** `/user/login/` (POST)
- **Generate Token:** `/api/generate-token/` (POST, Requires Authentication)
- **Update Access Token:** `/api/update-access-token/` (POST, Requires Authentication)
- **Call Dummy API in Another Project:** `/api/call-dummy-api/` (POST, Requires Authentication)
- **Call 3rd Party API:** `/api/call-3rd-party/` (POST, Requires Authentication)

## Usage

1. Register a new user using the `user/registration/` endpoint.
2. Log in using the `user/login/` endpoint to obtain access and refresh tokens.
3. Use the generated access token to authenticate requests to protected endpoints.
4. Use the `api/update-access-token/` endpoint to update the access token from the refresh token.
5. Explore other API endpoints based on your requirements.


## Technologies Used

- Django
- Django REST Framework
- OAuth2 Provider
- Simple JWT


