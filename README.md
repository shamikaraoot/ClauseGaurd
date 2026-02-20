# ClauseGuard 🛡️

**AI-Powered Terms & Conditions Analyzer**

ClauseGuard is a full-stack application that helps users understand Terms and Conditions documents by analyzing them for risky clauses, hidden fees, data collection practices, and more. It provides a simplified summary, risk assessment, and an interactive Q&A chatbot.

## Features

- 📄 **Text & URL Analysis**: Paste Terms & Conditions text or provide a URL to scrape
- 🌐 **Production-Ready Scraper**: Multi-strategy web scraping (requests → httpx → Playwright) handles bot detection, JavaScript rendering, and blocked requests
- 🤖 **AI-Powered Analysis**: Uses OpenAI GPT to detect payment clauses, auto-renewals, data collection, third-party sharing, and risky legal clauses
- ⚠️ **Risk Scoring**: Provides Low/Medium/High risk assessment with color-coded indicators
- 📋 **Alert System**: Generates bullet-point alerts for concerning clauses
- 💬 **Interactive Chatbot**: Ask follow-up questions about the analyzed document
- 🎨 **Modern UI**: Clean, minimal interface with gradient design

## Tech Stack

### Backend
- Python 3.10+
- FastAPI
- Uvicorn
- OpenAI API (optional - falls back to rule-based analysis)
- BeautifulSoup4 (web scraping)
- Requests (HTTP client)
- httpx (alternative HTTP client with HTTP/2 support)
- Playwright (JavaScript rendering for modern websites)
- Pydantic
- python-dotenv

### Frontend
- React 18
- Vite
- Axios
- Modern CSS with gradient design

## Project Structure

```
ClauseGuard/
│
├── backend/
│   ├── main.py              # FastAPI application
│   ├── analyzer.py          # NLP analysis logic
│   ├── scraper.py           # URL scraping functionality
│   ├── chatbot.py           # Q&A chatbot logic
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Environment variables template
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main React component
│   │   ├── App.css
│   │   ├── main.jsx         # React entry point
│   │   ├── index.css        # Global styles
│   │   ├── api.js           # API utility functions
│   │   └── components/
│   │       ├── AnalysisResult.jsx
│   │       ├── AnalysisResult.css
│   │       ├── ChatBox.jsx
│   │       └── ChatBox.css
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- Node.js 16+ and npm
- (Optional) OpenAI API key for enhanced AI analysis

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment:**
   ```bash
   # Windows PowerShell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers (required for JavaScript-rendered pages):**
   ```bash
   python -m playwright install
   ```
   
   Note: Playwright is used as a fallback when websites require JavaScript rendering or block standard HTTP requests. The scraper will work without it, but may fail on some modern websites.

4. **Set up environment variables:**
   ```bash
   # Copy the example file
   copy .env.example .env   # Windows
   cp .env.example .env     # macOS/Linux
   
   # Edit .env and add your OpenAI API key (optional)
   # OPENAI_API_KEY=your_key_here
   ```

5. **Run the backend server:**
   ```bash
   uvicorn main:app --reload
   ```
   
   The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Open a new terminal and navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```
   
   The frontend will be available at `http://localhost:5173`

### Running in Cursor

1. Open the project folder in Cursor
2. Backend: Open a terminal in Cursor, navigate to `backend`, activate venv, and run `uvicorn main:app --reload`
3. Frontend: Open another terminal, navigate to `frontend`, and run `npm run dev`

### Running in PyCharm

1. **Backend:**
   - Open the project folder in PyCharm
   - Configure Python interpreter: File → Settings → Project → Python Interpreter
   - Select or create a virtual environment
   - Install requirements: Open Terminal in PyCharm and run `pip install -r backend/requirements.txt`
   - Create a run configuration:
     - Script path: `backend/main.py`
     - Or run: `uvicorn main:app --reload` from `backend` directory

2. **Frontend:**
   - Open Terminal in PyCharm
   - Navigate to `frontend` directory
   - Run `npm install`
   - Run `npm run dev`

## API Endpoints

### `POST /analyze`
Analyze Terms and Conditions text or URL.

**Request:**
```json
{
  "text": "Terms and conditions text...",
  "url": "https://example.com/terms"
}
```

**Response:**
```json
{
  "summary": "Brief summary of the document...",
  "risk_score": "Low|Medium|High",
  "alerts": [
    "Contains automatic renewal clauses",
    "Shares data with third parties"
  ]
}
```

### `POST /chat`
Ask questions about the analyzed document.

**Request:**
```json
{
  "question": "What are the cancellation policies?",
  "context": "Summary text from analysis..."
}
```

**Response:**
```json
{
  "answer": "Based on the analysis..."
}
```

## Usage

1. **Start both backend and frontend servers** (see Setup Instructions)

2. **Open the frontend** in your browser (`http://localhost:5173`)

3. **Analyze a document:**
   - Paste Terms & Conditions text in the text area, OR
   - Enter a URL to the Terms & Conditions page
   - Click "Analyze"

4. **Review the results:**
   - Read the summary
   - Check the risk score (color-coded: Green=Low, Yellow=Medium, Red=High)
   - Review the alerts list

5. **Ask questions:**
   - Use the chatbot to ask follow-up questions
   - Click suggestion buttons for common questions
   - Type your own questions

## Notes

- **OpenAI API Key**: The application works without an API key using rule-based analysis, but for best results, add your OpenAI API key to `backend/.env`
- **CORS**: The backend is configured to accept requests from `localhost:5173` (Vite default) and `localhost:3000`
- **Error Handling**: The application includes comprehensive error handling and user-friendly error messages
- **Fallback Mode**: If OpenAI API is not available, the system automatically falls back to rule-based pattern matching
- **Web Scraping**: The scraper uses a multi-strategy approach:
  1. **Strategy 1**: Standard HTTP requests with browser headers
  2. **Strategy 2**: httpx with HTTP/2 support (if httpx is installed)
  3. **Strategy 3**: Playwright headless browser (if Playwright is installed)
  
  This ensures maximum compatibility with different websites, including those that:
  - Block automated requests (403 errors)
  - Require JavaScript rendering
  - Have bot detection systems
  - Use cookie consent pages
  
  The scraper automatically tries each strategy in order until one succeeds.

## Development

### Backend Development
- The backend uses FastAPI with automatic API documentation at `http://localhost:8000/docs`
- Hot reload is enabled with `--reload` flag

### Frontend Development
- Vite provides fast HMR (Hot Module Replacement)
- React Strict Mode is enabled for better development experience

## License

This project is for educational and demonstration purposes.

## Support

For issues or questions, please check:
- Backend logs in the terminal running `uvicorn`
- Frontend console in browser DevTools
- Network tab for API request/response details
