# Resume Backend API

Backend API for Aditya's portfolio website (theaditya.vercel.app) built with FastAPI.

## Overview

This project provides a RESTful API backend for a portfolio website with the following features:
- FastAPI-based routing system with modular architecture
- Data serving from JSON files
- AI agent system for content management and page behavior control
- Centralized configuration management
- Custom middleware for logging and CORS
- Comprehensive logging and development tracking

## Project Structure

```
resume-backend/
├── main.py                 # Main entry point
├── requirements.txt        # Python dependencies
├── development_log.txt     # Development changelog and tracking
├── data/                   # JSON data files
│   ├── intro.json
│   ├── jobs.json
│   ├── projects.json
│   ├── projects_new.json
│   ├── certificates.json
│   ├── layout.json
│   └── page.json
├── app/                    # Main application package
│   ├── __init__.py
│   ├── main.py            # FastAPI application setup
│   ├── config/            # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py    # Application settings
│   ├── models/            # Pydantic models
│   │   ├── __init__.py
│   │   └── schemas.py     # API request/response models
│   ├── routes/            # API route handlers
│   │   ├── __init__.py
│   │   ├── main.py       # Main routes (/health, /)
│   │   ├── data.py       # Data routes (/intro, /jobs, etc.)
│   │   └── ai.py         # AI routes (/ai/*)
│   ├── services/          # Business logic layer
│   │   ├── __init__.py
│   │   └── data_service.py # Data and AI services
│   ├── middleware/        # Custom middleware
│   │   ├── __init__.py
│   │   └── custom.py     # Logging and other middleware
│   └── utils/             # Utility functions
│       ├── __init__.py
│       └── data_loader.py # Data loading utilities
└── tests/                 # Test files
    └── __init__.py
```

## Quick Start

### Prerequisites
- Python 3.11+
- Virtual environment (automatically configured)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Aditya-AR-A/resume-backend.git
cd resume-backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the development server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, you can access:
- **Interactive API docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative docs**: http://localhost:8000/redoc

## API Endpoints

### Core Endpoints
- `GET /` - API information and status
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

### Data Endpoints
All data endpoints are prefixed with `/api`:
- `GET /api/intro` - Introduction data
- `GET /api/jobs` - Work experience data
- `GET /api/projects` - Projects data
- `GET /api/projects/new` - New projects data
- `GET /api/certificates` - Certificates data
- `GET /api/layout` - Page layout configuration
- `GET /api/page` - Page configuration

### AI System Endpoints (Placeholders)
All AI endpoints are prefixed with `/ai`:
- `POST /ai/analyze` - Content analysis (to be implemented)
- `POST /ai/generate` - Content generation (to be implemented)
- `GET /ai/status` - AI system status

## Architecture

The application follows a modular, layered architecture:

### Layers
1. **Routes Layer** (`app/routes/`): HTTP request handlers and API endpoints
2. **Services Layer** (`app/services/`): Business logic and data processing
3. **Models Layer** (`app/models/`): Data validation and serialization with Pydantic
4. **Utils Layer** (`app/utils/`): Helper functions and utilities
5. **Config Layer** (`app/config/`): Centralized configuration management
6. **Middleware Layer** (`app/middleware/`): Custom request/response processing

### Key Features
- **Separation of Concerns**: Each layer has a specific responsibility
- **Dependency Injection**: Services are injected into routes
- **Configuration Management**: Environment-based settings with pydantic-settings
- **Logging**: Comprehensive logging with custom middleware
- **Error Handling**: Proper HTTP status codes and error responses
- **Data Validation**: Pydantic models for all API requests/responses

## Development

### Logging
All development activities are tracked in `development_log.txt` with the following format:
```
[Date: YYYY-MM-DD HH:MM]
[Type: UPDATE/FEATURE/BUGFIX/DEBUG]
[Status: STARTED/IN_PROGRESS/COMPLETED/FAILED]
[Component: e.g., API/Routing/AI_System]
[Description: Brief description]
[Details: More detailed information]
[Next Steps: If applicable]
```

### Adding New Features
1. **Models**: Define Pydantic models in `app/models/schemas.py`
2. **Services**: Implement business logic in `app/services/`
3. **Routes**: Create route handlers in `app/routes/`
4. **Update Log**: Document changes in `development_log.txt`
5. **Test**: Verify functionality

### Data Files
The API serves data from JSON files in the `data/` directory. To add new data:
1. Create a new JSON file in the `data/` directory
2. Add corresponding Pydantic models in `app/models/schemas.py`
3. Implement service methods in `app/services/data_service.py`
4. Create route handlers in `app/routes/data.py`
5. Update the development log

## AI System Features

The backend includes an intelligent AI system with message classification and processing capabilities:

### 🤖 Message Classification
- **Question Detection**: Identifies questions with 70-100% confidence
- **Search Request Detection**: Recognizes search intents and filters
- **Intent Analysis**: Determines specific user intents (project inquiry, experience search, etc.)
- **Keyword Extraction**: Extracts relevant portfolio-related keywords
- **Entity Recognition**: Identifies technologies, years, and other entities

### 🧠 AI Endpoints

#### Enhanced AI Chat
```http
POST /ai/chat
```
Send natural language messages to the AI system with automatic classification and processing.

#### Message Classification
```http
POST /ai/classify
```
Classify messages without full processing - useful for frontend validation.

#### Question Answering
```http
POST /ai/ask
```
Dedicated endpoint for question-answering with context awareness.

#### Content Search
```http
POST /ai/search
```
Search through portfolio data with advanced filtering options.

#### Content Analysis
```http
POST /ai/analyze
```
Analyze content with intelligent classification and keyword extraction.

#### Content Generation
```http
POST /ai/generate
```
Generate content based on portfolio data and user context.

### 🎯 Message Types Detected

| Message Type | Confidence | Example |
|-------------|------------|---------|
| **Question** | 70-100% | "What projects have you worked on?" |
| **Search Request** | 70-90% | "Find certificates related to AWS" |
| **Command** | 50-80% | "Update my portfolio information" |
| **Statement** | 50-70% | "Hello, how are you?" |

### 🔧 Configuration

#### Environment Variables
Create a `.env` file based on `.env.example`:

```bash
# AI Configuration
USE_LOCAL_AI=false
USE_RENDER_AI=true
RENDER_API_KEY=your_render_api_key_here

# AI Features
ENABLE_CACHING=true
CACHE_TTL=3600
```

#### API Documentation
- **Swagger JSON**: `swagger.json` - Ready for frontend integration
- **Interactive Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### 🚀 Quick AI Test

Test the AI classification:

```bash
python test_ai_classification.py
```

This will demonstrate how the AI system classifies different types of messages and routes them to appropriate handlers.

## Deployment

### Local Development
```bash
python main.py
```

### Production
Use a production ASGI server like Uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker (Future)
Docker support will be added in future updates.

## Contributing

1. Follow the logging format in `development_log.txt`
2. Keep FastAPI patterns consistent
3. Add proper error handling
4. Update documentation

## License

This project is part of Aditya's portfolio website backend.

## Contact

For questions or contributions, please refer to the development log or create an issue in the repository.
