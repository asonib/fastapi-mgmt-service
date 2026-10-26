# FastAPI Management Service

Production-grade FastAPI microservice built with clean separation of concerns, structured logging, custom error handling, environment-specific configurations, and Swagger documentation.

## Python Version: `3.15.1`

***This project works with Ollama***

- Make sure you have ollama running in your local.
- Set the following env variables
    - OLLAMA_BASE_URL=`http://localhost:11434/v1`
    - OPENAI_API_KEY=`ollama`
- Then hit the `/summary` API

## Project Structure
- `app/config/`: Dynamic environment-based settings
- `app/controller/`: API routers / endpoints
- `app/service/`: Business logic and external API integrations
- `app/exception/`: Custom exception handlers
- `app/schema/`: Pydantic DTOs
- `app/utils/`: Logging and utilities
- `app/tests/`: Unit tests


## Environment Variables
Create `.env` file in project root. This project is configured to use `.env.dev`, `.env.test`, `.env.prod`
```bash
API_KEY=
MAX_SUMMARY_LENGTH=
OLLAMA_BASE_URL=
OPENAI_API_KEY=
OPENAI_MODEL_SEMVER=
WEATHER_API_KEY=
```

## Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
```

## Install Dependencies
```bash
pip install -r requirements.txt
```

### Development (Default)
```bash
uvicorn app.main:app --reload
```

### Test
```bash
ENVIRONMENT=test uvicorn app.main:app --reload
```

### Production
```bash
ENVIRONMENT=prod uvicorn app.main:app --reload
```

## API cURL

***Actuator API***
```bash
curl -X GET http://localhost:8000/actuator
```

***Weather API***
```bash
curl --location 'http://localhost:8000/weather?city=location'
```

***Joke API***
```bash
curl --location 'http://localhost:8000/joke'
```
***Summary API***
```bash
curl --location 'http://localhost:8000/summary' \
--header 'accept: application/json' \
--header 'Content-Type: application/json' \
--header 'X-API-Key: get-from-env' \
--data '{
    "text": "text"
}'
```

## Swagger and Redoc

***Swagger*** : 
http://localhost:8000/docs#/

***Redoc*** : 
http://localhost:8000/redoc
