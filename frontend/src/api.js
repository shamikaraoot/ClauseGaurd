import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

export const analyzeText = async (text, url) => {
  const response = await axios.post(`${API_BASE_URL}/analyze`, {
    text: text || null,
    url: url || null,
  })
  return response.data
}

export const chatQuestion = async (question, context) => {
  const response = await axios.post(`${API_BASE_URL}/chat`, {
    question,
    context,
  })
  return response.data
}
