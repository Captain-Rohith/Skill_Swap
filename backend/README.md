
# Skill Swap Platform Backend

A FastAPI-based backend for the Skill Swap Platform with PostgreSQL database and Clerk authentication.

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Database Setup**
   - Install PostgreSQL
   - Create a database named `skillswap`
   - Update `DATABASE_URL` in `.env` file

3. **Environment Variables**
   - Copy `.env.example` to `.env`
   - Add your Clerk secret key and database URL

4. **Run the Application**
   ```bash
   python main.py
   ```

## API Endpoints

### Authentication
All endpoints except `/users/search` require Clerk JWT authentication via `Authorization: Bearer <token>` header.

### User Management
- `POST /api/users/profile` - Create/update user profile
- `GET /api/users/profile` - Get current user profile
- `PUT /api/users/profile` - Update current user profile
- `GET /api/users/search?skill=python` - Search public users by skill (public)

### Swap Requests
- `POST /api/swaps/request` - Create swap request
- `GET /api/swaps/` - Get user's swaps (sent/received)
- `PATCH /api/swaps/{id}/accept` - Accept swap request
- `PATCH /api/swaps/{id}/reject` - Reject swap request
- `DELETE /api/swaps/{id}` - Delete swap request (owner only)

### Feedback
- `POST /api/swaps/{id}/feedback` - Submit feedback
- `GET /api/swaps/{id}/feedback` - Get swap feedback

### Admin (Optional)
- `GET /api/admin/users` - List all users
- `PATCH /api/admin/users/{id}/ban` - Ban user

## Database Models

- **User**: Profile data linked to Clerk ID
- **SwapRequest**: Skill exchange requests between users
- **Feedback**: Ratings and comments after completed swaps

## Security

- All user data is scoped by authenticated Clerk user ID
- Users can only access their own data in protected endpoints
- Public search only shows public profiles
- JWT tokens are verified for protected routes
