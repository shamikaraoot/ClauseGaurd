import React, { useState } from 'react'
import axios from 'axios'
import './App.css'
import AnalysisResult from './components/AnalysisResult'
import ChatBox from './components/ChatBox'

const API_BASE_URL = 'http://localhost:8000'

function App() {
  const [text, setText] = useState('')
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [analysisResult, setAnalysisResult] = useState(null)
  const [chatContext, setChatContext] = useState('')

  const handleAnalyze = async () => {
    if (!text.trim() && !url.trim()) {
      setError('Please provide either text or URL')
      return
    }

    setLoading(true)
    setError('')
    setAnalysisResult(null)
    setChatContext('')

    try {
      const response = await axios.post(`${API_BASE_URL}/analyze`, {
        text: text.trim() || null,
        url: url.trim() || null,
      })

      setAnalysisResult(response.data)
      setChatContext(response.data.summary)
    } catch (err) {
      let message =
        err?.response?.data?.detail ||
        err?.message ||
        'Failed to analyze. Please check your connection and try again.'

      // If user only provided a URL and the browser reports a generic
      // network error, explain that we may not be allowed to read the page.
      if (
        !text.trim() &&
        url.trim() &&
        !err?.response &&
        (err?.message || '').toLowerCase().includes('network error')
      ) {
        message =
          "We could not directly access this website's Terms & Conditions from your browser. " +
          "The site may not allow this kind of automated access or there may be network restrictions. " +
          "Permission to read the page may not be granted, so please copy and paste the Terms & Conditions text " +
          "manually and proceed with caution before accepting.";
      }

      setError(message)
    } finally {
      setLoading(false)
    }
  }

  const handleClear = () => {
    setText('')
    setUrl('')
    setError('')
    setAnalysisResult(null)
    setChatContext('')
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>🛡️ ClauseGuard</h1>
        <p>AI-Powered Terms & Conditions Analyzer</p>
      </header>

      <main className="app-main">
        <div className="input-section">
          <div className="input-group">
            <label htmlFor="text-input">Paste Terms & Conditions Text:</label>
            <textarea
              id="text-input"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Paste your Terms and Conditions text here..."
              rows={6}
              disabled={loading}
            />
          </div>

          <div className="divider">
            <span>OR</span>
          </div>

          <div className="input-group">
            <label htmlFor="url-input">Enter Terms & Conditions URL:</label>
            <input
              id="url-input"
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com/terms"
              disabled={loading}
            />
          </div>

          <div className="button-group">
            <button
              onClick={handleAnalyze}
              disabled={loading || (!text.trim() && !url.trim())}
              className="btn-primary"
            >
              {loading ? 'Analyzing...' : 'Analyze'}
            </button>
            <button
              onClick={handleClear}
              disabled={loading}
              className="btn-secondary"
            >
              Clear
            </button>
          </div>

          {error && (
            <div className="error-message">
              ⚠️ {error}
            </div>
          )}
        </div>

        {analysisResult && (
          <>
            <AnalysisResult result={analysisResult} />
            {chatContext && (
              <ChatBox context={chatContext} />
            )}
          </>
        )}
      </main>

      <footer className="app-footer">
        <p>ClauseGuard v1.0.0 - Analyze Terms & Conditions with AI</p>
      </footer>
    </div>
  )
}

export default App
