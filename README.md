# Blog Management System

A comprehensive FastAPI-based blog management system with CRUD operations, user authentication, likes, and comments functionality.

## Features

- **User Authentication**: JWT-based authentication with registration and login
- **Blog Post CRUD**: Complete Create, Read, Update, Delete operations for blog posts
- **Like System**: Users can like/unlike posts (one like per user per post)
- **Comment System**: Users can add and view comments on blog posts
- **Authorization**: Protected endpoints requiring authentication for write operations
- **Comprehensive API**: RESTful API with proper status codes and error handling

## Project Structure

```
backend-intern-crud/
├── src/
│   └── main.py                 # Main FastAPI application
├── requirements.txt            # Python dependencies
├── README.md                  # This file
├── postman_collection.json    # Postman collection for testing
└── .gitignore                 # Git ignore file
```

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/backend-intern-crud.git
   cd backend-intern-crud
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   cd src
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Access the application**
   - API Base URL: `http://localhost:8000`
   - Interactive API Documentation (Swagger UI): `http://localhost:8000/docs`
   - Alternative API Documentation (ReDoc): `http://localhost:8000/redoc`

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Register a new user | No |
| POST | `/api/auth/login` | Login user and get JWT token | No |

### Blog Posts

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/posts` | Create a new blog post | Yes |
| GET | `/api/posts` | Get all blog posts | No |
| GET | `/api/posts/{id}` | Get a specific blog post | No |
| PUT | `/api/posts/{id}` | Update a blog post | Yes (Author only) |
| DELETE | `/api/posts/{id}` | Delete a blog post | Yes (Author only) |

### Likes

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/posts/{id}/like` | Like a blog post | Yes |
| DELETE | `/api/posts/{id}/like` | Unlike a blog post | Yes |

### Comments

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/posts/{id}/comment` | Add a comment to a blog post | Yes |
| GET | `/api/posts/{id}/comments` | Get all comments for a blog post | No |

### Health Check

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/health` | Check API health status | No |

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. To access protected endpoints:

1. Register a user using `/api/auth/register`
2. Login using `/api/auth/login` to get an access token
3. Include the token in the Authorization header: `Bearer <your-token>`

### Example Authentication Flow

```bash
# 1. Register a user
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword"
  }'

# 2. Login to get token
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpassword"
  }'

# 3. Use token for protected endpoints
curl -X POST "http://localhost:8000/api/posts" \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Post",
    "content": "This is my first blog post!"
  }'
```

## Request/Response Examples

### Create Blog Post

**Request:**
```json
POST /api/posts
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Understanding FastAPI",
  "content": "FastAPI is a modern, fast web framework for building APIs with Python 3.7+..."
}
```

**Response:**
```json
{
  "id": 1,
  "title": "Understanding FastAPI",
  "content": "FastAPI is a modern, fast web framework for building APIs with Python 3.7+...",
  "author": "testuser",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "likes_count": 0,
  "comments_count": 0
}
```

### Like a Post

**Request:**
```json
POST /api/posts/1/like
Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "Post liked successfully",
  "likes_count": 1
}
```

### Add Comment

**Request:**
```json
POST /api/posts/1/comment
Authorization: Bearer <token>
Content-Type: application/json

{
  "content": "Great post! Very informative."
}
```

**Response:**
```json
{
  "id": 1,
  "content": "Great post! Very informative.",
  "author": "testuser",
  "post_id": 1,
  "created_at": "2024-01-15T11:00:00Z"
}
```

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- `200` - OK
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error

Example error response:
```json
{
  "detail": "Post not found"
}
```

## Testing with Postman

Import the `postman_collection.json` file in Postman to test all endpoints. The collection includes:

- Pre-configured requests for all endpoints
- Environment variables for base URL and tokens
- Examples of authorized vs unauthorized requests
- Sample request bodies and expected responses

## Data Storage

**Note**: This implementation uses in-memory storage for simplicity. In a production environment, you should integrate with a proper database like PostgreSQL, MySQL, or MongoDB.

## Security Considerations

- JWT tokens expire after 30 minutes
- Passwords are hashed using bcrypt
- Protected endpoints require valid JWT tokens
- Users can only modify their own posts
- Input validation using Pydantic models

## Future Enhancements

- Database integration (PostgreSQL, MongoDB)
- User profile management
- Post categories and tags
- Search functionality
- Pagination for large datasets
- Rate limiting
- Email verification
- Password reset functionality
- File upload for images
- Rich text editor support

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is for educational purposes as part of the LawVriksh backend internship assignment.

## Support

For questions or issues, please contact the development team or create an issue in the repository.