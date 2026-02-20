import React from 'react'
import './AnalysisResult.css'

function AnalysisResult({ result }) {
  const getRiskColor = (riskScore) => {
    switch (riskScore) {
      case 'Low':
        return '#4caf50'
      case 'Medium':
        return '#ff9800'
      case 'High':
        return '#f44336'
      default:
        return '#757575'
    }
  }

  const getRiskBgColor = (riskScore) => {
    switch (riskScore) {
      case 'Low':
        return '#e8f5e9'
      case 'Medium':
        return '#fff3e0'
      case 'High':
        return '#ffebee'
      default:
        return '#f5f5f5'
    }
  }

  return (
    <div className="analysis-result">
      <div className="result-card">
        <h2>Analysis Summary</h2>
        <p className="summary-text">{result.summary}</p>
      </div>

      <div className="result-card">
        <h2>Risk Assessment</h2>
        <div
          className="risk-badge"
          style={{
            backgroundColor: getRiskBgColor(result.risk_score),
            color: getRiskColor(result.risk_score),
            borderColor: getRiskColor(result.risk_score),
          }}
        >
          <span className="risk-label">Risk Score:</span>
          <span className="risk-value">{result.risk_score}</span>
        </div>
      </div>

      <div className="result-card">
        <h2>⚠️ Alerts & Concerns</h2>
        <ul className="alerts-list">
          {result.alerts.map((alert, index) => (
            <li key={index} className="alert-item">
              {alert}
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}

export default AnalysisResult
