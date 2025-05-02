# Pedagoggles AR
AR Classroom Assistant build for the Snap Spectacles

A real-time classroom assistance system that provides live captioning, translation, and note-taking through AR glasses.
![Screenshot 2025-04-27 at 12 29 37 PM](https://github.com/user-attachments/assets/c8e77e48-54cf-4195-8b93-28942cb6895b)

## Features

- Real-time speech-to-text transcription using WebSockets
- AI-powered lecture summarization with Gemini AI
- Auto-generated questions based on lecture content
- Frontend for audio recording and real-time processing

## Project Structure

```
/backend - FastAPI server with speech recognition and AI capabilities
/frontend - React TypeScript application for audio capture and processing
/Spectacles - Lens Studio assets
```

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file with:
   ```
   MONGODB_URL=your_mongodb_connection_string
   DATABASE_NAME=your_database_name
   GEMINI_API_KEY=your_gemini_api_key
   ```

4. Start the server:
   ```
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Edit the config.ts file to set your endpoints and user ID:
   ```
   src/config.ts
   ```

4. Start the development server:
   ```
   npm start
   ```

## API Endpoints

- `/api/startLecture` - Start a new lecture session
- `/api/updateInfo` - Update lecture with new audio/images
- `/api/requestSummary` - Get AI-generated summary of lecture
- `/api/requestQuestions` - Get AI-generated questions
- `/ws/{client_id}` - WebSocket endpoint for real-time transcription

## Technologies Used

- FastAPI (Backend)
- React with TypeScript (Frontend)
- Google Gemini AI
- MongoDB
- Snapchat Lens Studio
- WebSockets for real-time communication


## Credits
- Settings Icon CC-BY 3.0: [Game-Icons.net](https://game-icons.net/)
