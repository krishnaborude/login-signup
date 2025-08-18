# FastAPI Authentication API

A robust authentication API built with FastAPI and PostgreSQL that provides secure user registration and login functionality.

🌐 **Live API**: [https://login-signup-r2s9.onrender.com](https://login-signup-r2s9.onrender.com)
- API Documentation: [https://login-signup-r2s9.onrender.com/docs](https://login-signup-r2s9.onrender.com/docs)
- Alternative Documentation: [https://login-signup-r2s9.onrender.com/redoc](https://login-signup-r2s9.onrender.com/redoc)

## Features

- 🔐 User Registration (Signup)
- 🔑 User Authentication (Login)
- 📧 Support for both username and email login
- 🔒 Secure password hashing using bcrypt
- 🎟️ JWT token-based authentication
- 🛡️ Input validation using Pydantic
- 📦 PostgreSQL database with SQLAlchemy ORM
- 🚀 Async API endpoints
- 📝 Interactive API documentation

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **PostgreSQL**: Robust, open-source database
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation using Python type annotations
- **JWT**: JSON Web Token for secure authentication
- **Bcrypt**: Secure password hashing
- **Uvicorn**: Lightning-fast ASGI server

## Prerequisites

- Python 3.10+
- PostgreSQL
- pip (Python package manager)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/krishnaborude/login-signup.git
   cd login-signup
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - Unix/MacOS:
     ```bash
     source .venv/bin/activate
     ```

4. Install required packages:
   ```bash
   pip install fastapi uvicorn sqlalchemy pydantic passlib python-jose python-multipart psycopg2-binary python-dotenv bcrypt email-validator requests
   ```

5. Create a `.env` file in the root directory with the following content:
   ```env
   DATABASE_URL=postgresql://postgres:your_password@localhost:5432/auth_db
   SECRET_KEY=your_secret_key_here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```
   Replace `your_password` with your PostgreSQL password and generate a secure `SECRET_KEY`.

## Database Setup

1. Create a PostgreSQL database named `auth_db`:
   ```sql
   CREATE DATABASE auth_db;
   ```

2. The tables will be automatically created when you start the application.

## Running the Application

1. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```

2. The API will be available at: http://127.0.0.1:8000

3. Access the interactive API documentation at: http://127.0.0.1:8000/docs

## API Endpoints

### 1. User Registration (Signup)
- **Endpoint**: `/signup`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "username": "your_username",
    "email": "your_email@example.com",
    "password": "your_password"
  }
  ```
- **Response**:
  ```json
  {
    "username": "your_username",
    "email": "your_email@example.com",
    "id": "generated-uuid"
  }
  ```

### 2. User Login
- **Endpoint**: `/login`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "username": "your_username_or_email",
    "password": "your_password"
  }
  ```
- **Response**:
  ```json
  {
    "access_token": "jwt_token",
    "token_type": "bearer"
  }
  ```

## Features in Detail

### Security
- Passwords are hashed using bcrypt before storage
- JWT tokens are used for authentication
- Token expiration time is configurable (default: 30 minutes)
- Environment variables for sensitive information

### Validation
- Email format validation
- Username uniqueness check
- Password requirements enforcement
- Input data validation using Pydantic models

### User-Friendly Features
- Login with either username or email
- Clear error messages
- Interactive API documentation
- Example requests and responses

## Error Handling

The API provides clear error messages for various scenarios:
- User already exists
- Invalid credentials
- Invalid email format
- Database connection issues
- Missing required fields

## Testing the API

You can test the API using:

1. **Swagger UI**: Visit http://127.0.0.1:8000/docs
2. **ReDoc**: Visit http://127.0.0.1:8000/redoc


## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- FastAPI documentation
- SQLAlchemy documentation
- PostgreSQL documentation
- Python-Jose for JWT handling
- Passlib for password hashing
