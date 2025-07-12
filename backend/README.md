# Skill Swap Backend API

A FastAPI backend for the Skill Swap Platform that allows users to list skills they offer, request skills they want, and swap skills with other users.

## Features

- **User Management**: Profile creation, updates, privacy settings
- **Skill System**: Add/remove skills, categorize as offered/wanted
- **Search & Discovery**: Find users by skills, location, availability
- **Swap System**: Request, accept, reject, complete swaps
- **Rating System**: Rate users after completed swaps
- **Admin Panel**: User management, content moderation, analytics
- **Authentication**: Frontend-based authentication with user ID headers

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: Frontend-based (Clerk integration handled in frontend)
- **Migrations**: Alembic
- **Validation**: Pydantic

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── database.py            # Database configuration and session management
├── models.py              # SQLAlchemy database models
├── schemas.py             # Pydantic request/response schemas
├── requirements.txt       # Python dependencies
├── alembic.ini           # Alembic configuration
├── .env.example          # Environment variables template
├── routers/              # API route handlers
│   ├── __init__.py
│   ├── users.py          # User management endpoints
│   ├── skills.py         # Skill management endpoints
│   ├── swaps.py          # Swap request endpoints
│   └── admin.py          # Admin panel endpoints
├── utils/                # Utility functions
│   ├── __init__.py
│   └── auth.py           # Authentication utilities
└── alembic/              # Database migrations
    ├── __init__.py
    ├── env.py
    ├── script.py.mako
    └── versions/
```

## Setup Instructions

### 1. Prerequisites

- Python 3.8+
- PostgreSQL database

### 2. Environment Setup

Create a `.env` file in the backend directory with the following variables:

```env
# Database Configuration
DATABASE_URL=postgresql://rv:rv@localhost:5432/SkillSwap

# Admin Configuration
ADMIN_USER_IDS=admin_user_id_1,admin_user_id_2

# Server Configuration
PORT=8000

# Environment
ENVIRONMENT=development
```

### 3. Database Setup

1. Create a PostgreSQL database named `SkillSwap`
2. Create a user `rv` with password `rv` (or update the DATABASE_URL accordingly)

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Database Migrations

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 6. Run the Application

```bash
# Development mode
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:

- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Users (`/api/users/`)

- `POST /` - Create user profile
- `GET /me` - Get current user profile
- `PUT /me` - Update user profile
- `GET /search` - Search users by skills
- `GET /{user_id}` - Get specific user profile (if public)

### Skills (`/api/skills/`)

- `GET /` - Get all skills
- `POST /` - Create new skill (admin only)
- `GET /search` - Search skills by name
- `POST /user-skills` - Add skill to user (offered/wanted)
- `DELETE /user-skills/{id}` - Remove skill from user
- `GET /user-skills/me` - Get current user's skills

### Swaps (`/api/swaps/`)

- `POST /` - Create swap request
- `GET /` - Get user's swap requests (sent/received)
- `PUT /{swap_id}/accept` - Accept swap request
- `PUT /{swap_id}/reject` - Reject swap request
- `PUT /{swap_id}/complete` - Mark swap as completed
- `DELETE /{swap_id}` - Cancel/delete swap request
- `POST /{swap_id}/rate` - Rate completed swap

### Admin (`/api/admin/`)

- `GET /users` - Get all users with pagination
- `PUT /users/{user_id}/ban` - Ban/unban user
- `GET /swaps` - Get all swaps with filters
- `GET /reports` - Get platform statistics
- `POST /broadcast` - Send platform-wide message

## Authentication

The API expects user authentication to be handled by the frontend. All protected endpoints require a user ID to be passed in the request header:

```
X-User-ID: <user_id>
```

The frontend should handle Clerk authentication and pass the user ID to the backend for user identification.

## Database Schema

### Users Table
- `clerk_user_id` (primary key, string)
- `name` (string)
- `email` (string, unique)
- `location` (string, optional)
- `profile_photo_url` (string, optional)
- `availability` (string, optional)
- `is_public` (boolean, default True)
- `is_banned` (boolean, default False)
- `created_at` (timestamp)
- `updated_at` (timestamp)

### Skills Table
- `id` (primary key)
- `name` (string, unique)
- `category` (string, optional)
- `created_at` (timestamp)

### UserSkills Table (Many-to-Many)
- `id` (primary key)
- `user_id` (foreign key to Users.clerk_user_id)
- `skill_id` (foreign key to Skills)
- `skill_type` (enum: "offered", "wanted")
- `proficiency_level` (string, optional)
- `created_at` (timestamp)

### SwapRequests Table
- `id` (primary key)
- `requester_id` (foreign key to Users.clerk_user_id)
- `requested_user_id` (foreign key to Users.clerk_user_id)
- `offered_skill_id` (foreign key to Skills)
- `requested_skill_id` (foreign key to Skills)
- `status` (enum: "pending", "accepted", "rejected", "completed", "cancelled")
- `message` (text, optional)
- `created_at` (timestamp)
- `updated_at` (timestamp)

### Ratings Table
- `id` (primary key)
- `swap_request_id` (foreign key to SwapRequests)
- `rater_id` (foreign key to Users.clerk_user_id)
- `rated_user_id` (foreign key to Users.clerk_user_id)
- `rating` (integer, 1-5)
- `feedback` (text, optional)
- `created_at` (timestamp)

## Response Format

All API responses follow this structure:

```json
{
  "success": true,
  "data": {...},
  "message": "Success message",
  "errors": []
}
```

## Error Handling

The API includes comprehensive error handling with appropriate HTTP status codes:

- `400 Bad Request` - Invalid input data
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server-side errors

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Code Formatting

```bash
# Install formatting tools
pip install black isort

# Format code
black .
isort .
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Production Deployment

For production deployment, consider:

1. **Environment Variables**: Use proper environment variable management
2. **Database**: Use a managed PostgreSQL service
3. **Authentication**: Ensure secure user ID validation in frontend
4. **CORS**: Restrict CORS origins to your frontend domain
5. **Logging**: Implement proper logging and monitoring
6. **Security**: Use HTTPS, rate limiting, and input validation
7. **Performance**: Add caching and database optimization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License. 