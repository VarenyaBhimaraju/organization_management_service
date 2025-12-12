# organization_management_service

A production-ready multi-tenant organization management system built with FastAPI and MongoDB.

## Live Demo

**API Documentation:** http://localhost:8000/docs

## Features

- Multi-tenant architecture with dynamic collections
- JWT authentication with bcrypt password hashing
- Automatic API documentation (Swagger/ReDoc)
- Docker support
- Comprehensive input validation
- Test suite included

## Tech Stack

- **Backend:** FastAPI (Python 3.11)
- **Database:** MongoDB 6.0
- **Authentication:** JWT + bcrypt
- **Containerization:** Docker

## API Endpoints

### Organization Management
- `POST /org/create` - Create new organization
- `GET /org/get` - Get organization details
- `PUT /org/update` - Update organization (requires auth)
- `DELETE /org/delete` - Delete organization (requires auth)

### Authentication
- `POST /admin/login` - Admin login
- `GET /admin/me` - Get current admin info (requires auth)

### Health
- `GET /health` - Health check
- `GET /` - API information

### Using Docker 

\`\`\`bash
# Start all services
docker-compose up -d

# Access API docs
open http://localhost:8000/docs
\`\`\`

### Local Development

\`\`\`bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start MongoDB
brew services start mongodb-community

# Run application
uvicorn app.main:app --reload
\`\`\`

## Testing

\`\`\`bash
# Run test suite
pytest tests/ -v

# Test with curl
curl -X POST http://localhost:8000/org/create \\
  -H "Content-Type: application/json" \\
  -d '{
    "organization_name": "test_company",
    "email": "admin@test.com",
    "password": "TestPass123!"
  }'
\`\`\`

## Architecture

\`\`\`
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── models/              # Pydantic models
│   ├── services/            # Business logic
│   ├── routes/              # API endpoints
│   ├── utils/               # Utilities (JWT, security)
│   └── database/            # MongoDB connection
└── tests/                   # Test suite
\`\`\`

## Security Features

- Password hashing with bcrypt (12 rounds)
- JWT token-based authentication
- Input validation with Pydantic
- Environment variable configuration
- Request validation and sanitization
