# Running Crop AI Project Locally

## Quick Start (Easiest Method)

### Method 1: Use the Batch Files
1. **Start Backend**: Double-click `start_backend.bat`
2. **Start Frontend**: Double-click `start_frontend.bat` (in a new terminal)

### Method 2: Manual Commands

#### Terminal 1 - Backend Server
```bash
cd "C:\Users\vansh\OneDrive\coding\AI-crop-recommendation"
venv\Scripts\activate
python app.py
```

#### Terminal 2 - Frontend Server
```bash
cd "C:\Users\vansh\OneDrive\coding\AI-crop-recommendation\frontend"
npm start
```

## Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000

## Troubleshooting
- Make sure you're in the correct directory
- Backend should show: "Running on http://127.0.0.1:5000"
- Frontend should show: "webpack compiled successfully"

## Project Structure
```
AI-crop-recommendation/
├── app.py                 # Flask backend
├── start_backend.bat      # Easy backend starter
├── start_frontend.bat     # Easy frontend starter
├── frontend/              # React frontend
│   ├── package.json
│   └── src/
└── venv/                  # Python virtual environment
```
