import React, { useState } from 'react'
import axios from 'axios'
import './ChatBox.css'

const API_BASE_URL = 'http://localhost:8000'

function ChatBox({ context }) {
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!question.trim()) {
      return
    }

    const userMessage = question.trim()
    setQuestion('')
    setLoading(true)
    setError('')

    // Add user message to chat
    const newMessages = [...messages, { role: 'user', content: userMessage }]
    setMessages(newMessages)

    try {
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        question: userMessage,
        context: context,
      })

      const assistantMessage = {
        role: 'assistant',
        content: response.data.answer,
      }

      setMessages([...newMessages, assistantMessage])
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.message ||
        'Failed to get response. Please try again.'
      )
      // Remove the user message if there was an error
      setMessages(messages)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="chatbox">
      <div className="chatbox-header">
        <h2>💬 Ask Questions</h2>
        <p>Get answers about the analyzed Terms & Conditions</p>
      </div>

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="empty-state">
            <p>Ask a question about the Terms & Conditions to get started!</p>
            <div className="suggestions">
              <button
                onClick={() => setQuestion('What are the cancellation policies?')}
                className="suggestion-btn"
              >
                What are the cancellation policies?
              </button>
              <button
                onClick={() => setQuestion('How is my data collected and shared?')}
                className="suggestion-btn"
              >
                How is my data collected and shared?
              </button>
              <button
                onClick={() => setQuestion('Are there any automatic renewals?')}
                className="suggestion-btn"
              >
                Are there any automatic renewals?
              </button>
            </div>
          </div>
        ) : (
          messages.map((msg, index) => (
            <div
              key={index}
              className={`message ${msg.role === 'user' ? 'message-user' : 'message-assistant'}`}
            >
              <div className="message-content">{msg.content}</div>
            </div>
          ))
        )}

        {loading && (
          <div className="message message-assistant">
            <div className="message-content">
              <span className="typing-indicator">Thinking...</span>
            </div>
          </div>
        )}

        {error && (
          <div className="chat-error">
            ⚠️ {error}
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="chat-input-form">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question about the Terms & Conditions..."
          disabled={loading}
          className="chat-input"
        />
        <button
          type="submit"
          disabled={loading || !question.trim()}
          className="chat-send-btn"
        >
          Send
        </button>
      </form>
    </div>
  )
}

export default ChatBox
