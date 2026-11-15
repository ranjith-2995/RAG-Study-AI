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
  async askQuestion(question, selectedDocId = null) {
    const res = await client.post('/api/chat', {
      question,
      selected_doc_id: selectedDocId,
    });
    return res.data;
  },

  // Summary
  async getSummary(docId = null) {
    const res = await client.post('/api/summary', {
      doc_id: docId,
    });
    return res.data;
  },
};

export default api;

