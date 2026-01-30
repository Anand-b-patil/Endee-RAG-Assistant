import axios from 'axios';

// Configure base URL for the API
// In production, this should be set via environment variable
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface AskResponse {
  answer: string;
  sources: Array<{
    text: string;
    metadata?: Record<string, any>;
  }>;
}

export interface UploadResponse {
  message: string;
  filename: string;
}

// API Methods
export const uploadDocument = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await api.post<UploadResponse>('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(
        error.response?.data?.error || 'Failed to upload document'
      );
    }
    throw new Error('An unexpected error occurred during upload');
  }
};

export const askQuestion = async (question: string): Promise<AskResponse> => {
  try {
    const response = await api.post<AskResponse>('/ask', { question });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(
        error.response?.data?.error || 'Failed to get answer'
      );
    }
    throw new Error('An unexpected error occurred while asking question');
  }
};

export default api;
