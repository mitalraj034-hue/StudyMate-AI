const API_BASE_URL = import.meta.env.VITE_API_URL || (typeof window !== 'undefined' && (window.location.port === '5173' || window.location.port === '8000') ? '/api' : 'http://127.0.0.1:8000/api');

function getAuthHeader() {
  const token = localStorage.getItem('studymate_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function handleResponse(res) {
  if (!res.ok) {
    let errorDetail = 'Request failed';
    try {
      const data = await res.json();
      errorDetail = data.detail || data.message || errorDetail;
    } catch (e) {
      // not json
    }
    throw new Error(errorDetail);
  }
  return res.json();
}

export const api = {
  // Auth
  async register(payload) {
    const res = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return handleResponse(res);
  },

  async login(payload) {
    const res = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return handleResponse(res);
  },

  async getMe() {
    const res = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: { ...getAuthHeader() }
    });
    return handleResponse(res);
  },

  async updateProfile(payload) {
    const res = await fetch(`${API_BASE_URL}/auth/profile`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
      body: JSON.stringify(payload)
    });
    return handleResponse(res);
  },

  async forgotPassword(email) {
    const res = await fetch(`${API_BASE_URL}/auth/forgot-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });
    return handleResponse(res);
  },

  // Documents
  async uploadDocument(file, onProgress) {
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(`${API_BASE_URL}/documents/upload`, {
      method: 'POST',
      headers: { ...getAuthHeader() },
      body: formData
    });
    return handleResponse(res);
  },

  async getDocuments(search = '') {
    const url = search ? `${API_BASE_URL}/documents?query=${encodeURIComponent(search)}` : `${API_BASE_URL}/documents`;
    const res = await fetch(url, {
      headers: { ...getAuthHeader() }
    });
    return handleResponse(res);
  },

  async getDocument(docId) {
    const res = await fetch(`${API_BASE_URL}/documents/${docId}`, {
      headers: { ...getAuthHeader() }
    });
    return handleResponse(res);
  },

  async deleteDocument(docId) {
    const res = await fetch(`${API_BASE_URL}/documents/${docId}`, {
      method: 'DELETE',
      headers: { ...getAuthHeader() }
    });
    return handleResponse(res);
  },

  // RAG / Chat
  async chatWithDocument(documentId, query, options = {}) {
    const payload = {
      document_id: documentId,
      query: typeof query === 'string' ? query : query?.query,
      custom_api_key: options.customApiKey || null,
      mode: options.mode || 'Detailed Explanation',
      level: options.level || 'Intermediate',
      language: options.language || 'English',
      action: options.action || null
    };
    const res = await fetch(`${API_BASE_URL}/rag/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
      body: JSON.stringify(payload)
    });
    return handleResponse(res);
  },

  async getChatHistory(docId) {
    const res = await fetch(`${API_BASE_URL}/rag/chat/${docId}/history`, {
      headers: { ...getAuthHeader() }
    });
    return handleResponse(res);
  },

  async clearChatHistory(documentId) {
    const res = await fetch(`${API_BASE_URL}/rag/chat/${documentId}/history`, {
      method: 'DELETE',
      headers: { ...getAuthHeader() }
    });
    return handleResponse(res);
  },

  async generateSummary(documentId, options = {}) {
    const payload = {
      document_id: documentId,
      summary_type: options.summaryType || options.summary_type || 'Detailed Summary',
      length: options.length || 'Detailed',
      topic: options.topic || null,
      level: options.level || 'Intermediate',
      language: options.language || 'English',
      action: options.action || null
    };
    const res = await fetch(`${API_BASE_URL}/rag/summary`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
      body: JSON.stringify(payload)
    });
    return handleResponse(res);
  },

  // Quizzes
  async generateQuiz(documentId, count = 5, difficulty = 'Medium', title = null, topic = null) {
    const res = await fetch(`${API_BASE_URL}/quiz/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
      body: JSON.stringify({
        document_id: documentId,
        count,
        difficulty,
        title,
        topic
      })
    });
    return handleResponse(res);
  },

  async getQuiz(quizId) {
    const res = await fetch(`${API_BASE_URL}/quiz/${quizId}`, {
      headers: { ...getAuthHeader() }
    });
    return handleResponse(res);
  },

  async submitQuiz(quizId, answers, timeSpentSeconds = 60) {
    const res = await fetch(`${API_BASE_URL}/quiz/${quizId}/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
      body: JSON.stringify({
        answers,
        time_spent_seconds: timeSpentSeconds
      })
    });
    return handleResponse(res);
  },

  async getQuizzesForDocument(docId) {
    const res = await fetch(`${API_BASE_URL}/quiz/document/${docId}`, {
      headers: { ...getAuthHeader() }
    });
    return handleResponse(res);
  },

  // Flashcards
  async generateFlashcards(documentId, count = 8, topic = null) {
    const res = await fetch(`${API_BASE_URL}/flashcards/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
      body: JSON.stringify({
        document_id: documentId,
        count,
        topic
      })
    });
    return handleResponse(res);
  },

  async getFlashcards(docId) {
    const res = await fetch(`${API_BASE_URL}/flashcards/document/${docId}`, {
      headers: { ...getAuthHeader() }
    });
    return handleResponse(res);
  },

  async updateFlashcardMastery(cardId, status) {
    const res = await fetch(`${API_BASE_URL}/flashcards/${cardId}/mastery`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
      body: JSON.stringify({ status })
    });
    return handleResponse(res);
  },

  // Progress
  async getDashboardStats() {
    const res = await fetch(`${API_BASE_URL}/progress/dashboard-stats`, {
      headers: { ...getAuthHeader() }
    });
    return handleResponse(res);
  },

  // Settings
  async getSettings() {
    const res = await fetch(`${API_BASE_URL}/settings`, {
      headers: { ...getAuthHeader() }
    });
    return handleResponse(res);
  },

  async updateSettings(payload) {
    const res = await fetch(`${API_BASE_URL}/settings/keys`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
      body: JSON.stringify(payload)
    });
    return handleResponse(res);
  },

  // Google Gemini AI Endpoints
  gemini: {
    async chat({ message, history = [], documentId = null, systemInstruction = null }) {
      const res = await fetch(`${API_BASE_URL}/gemini/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
        body: JSON.stringify({
          message,
          history,
          document_id: documentId,
          system_instruction: systemInstruction
        })
      });
      return handleResponse(res);
    },

    async ask({ question, documentId = null, context = null }) {
      const res = await fetch(`${API_BASE_URL}/gemini/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
        body: JSON.stringify({
          question,
          document_id: documentId,
          context
        })
      });
      return handleResponse(res);
    },

    async generateNotes({ topic = null, content = null, documentId = null, style = 'comprehensive' }) {
      const res = await fetch(`${API_BASE_URL}/gemini/notes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
        body: JSON.stringify({
          topic,
          content,
          document_id: documentId,
          style
        })
      });
      return handleResponse(res);
    },

    async summarize({ content = null, documentId = null, summaryType = 'executive', maxLength = null }) {
      const res = await fetch(`${API_BASE_URL}/gemini/summarize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
        body: JSON.stringify({
          content,
          document_id: documentId,
          summary_type: summaryType,
          max_length: maxLength
        })
      });
      return handleResponse(res);
    },

    async generateMCQ({ topic = null, content = null, documentId = null, count = 5, difficulty = 'Medium' }) {
      const res = await fetch(`${API_BASE_URL}/gemini/mcq`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
        body: JSON.stringify({
          topic,
          content,
          document_id: documentId,
          count,
          difficulty
        })
      });
      return handleResponse(res);
    },

    async generateQuiz({ topic = null, content = null, documentId = null, title = null, count = 5, difficulty = 'Medium', saveToDb = false }) {
      const res = await fetch(`${API_BASE_URL}/gemini/quiz`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
        body: JSON.stringify({
          topic,
          content,
          document_id: documentId,
          title,
          count,
          difficulty,
          save_to_db: saveToDb
        })
      });
      return handleResponse(res);
    }
  }
};
