import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000, // 2 minutes for model inference & embeddings
});

export const api = {
  // Stats
  async getStats() {
    const res = await client.get('/api/stats');
    return res.data;
  },

  // Health
  async getHealth() {
    const res = await client.get('/api/health');
    return res.data;
  },

  // Documents
  async getDocuments() {
    const res = await client.get('/api/documents');
    return res.data;
  },

  async uploadDocument(file, onProgress) {
    const formData = new FormData();
    formData.append('file', file);

    const res = await client.post('/api/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(percentCompleted);
        }
      },
    });
    return res.data;
  },

  async deleteDocument(docId) {
    const res = await client.delete(`/api/documents/${docId}`);
    return res.data;
  },

  // Chat
  async askQuestion(question, selectedDocId = null, history = [], language = 'English') {
    const res = await client.post('/api/chat', {
      question,
      selected_doc_id: selectedDocId,
      history,
      language,
    });
    return res.data;
  },

  // Summary
  async getSummary(docId = null, language = 'English') {
    const res = await client.post('/api/summary', {
      doc_id: docId,
      language,
    });
    return res.data;
  },

  async generateQuiz(docId, difficulty, count = 5) {
    const res = await client.post('/api/learning/quizzes', { doc_id: docId, difficulty, count });
    return res.data;
  },

  async submitQuiz(quizId, answers) {
    const res = await client.post(`/api/learning/quizzes/${quizId}/submit`, { answers });
    return res.data;
  },

  async generateFlashcards(docId, count = 8) {
    const res = await client.post('/api/learning/flashcards', { doc_id: docId, count });
    return res.data;
  },

  async getFlashcards(docId = null) {
    const res = await client.get('/api/learning/flashcards', { params: docId ? { doc_id: docId } : {} });
    return res.data;
  },

  async rateFlashcard(cardId, rating) {
    const res = await client.patch(`/api/learning/flashcards/${cardId}`, { rating });
    return res.data;
  },

  async generateMindmap(docId) {
    const res = await client.post('/api/learning/mindmap', { doc_id: docId });
    return res.data;
  },

  async generatePlan(docId, goal) {
    const res = await client.post('/api/learning/planner', { doc_id: docId, goal });
    return res.data;
  },

  async getPlan() {
    const res = await client.get('/api/learning/planner');
    return res.data.plan;
  },

  async updatePlanTopic(topicId, completed) {
    const res = await client.patch(`/api/learning/planner/topics/${topicId}`, { completed });
    return res.data;
  },

  async getAnalytics() {
    const res = await client.get('/api/learning/analytics');
    return res.data;
  },

  async recordStudyTime(seconds) {
    const res = await client.post('/api/learning/analytics/study-time', { seconds });
    return res.data;
  },

  getDocumentFileUrl(docId, page) {
    return `${API_BASE_URL}/api/documents/${docId}/file#page=${page}`;
  },
};

export default api;

