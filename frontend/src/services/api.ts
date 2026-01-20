/**
 * API service for communicating with the backend.
 */

import axios from 'axios';
import type { ProcessResponse, AnswerResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const apiService = {
    /**
     * Process news article URLs.
     */
    async processUrls(urls: string[]): Promise<ProcessResponse> {
        const response = await api.post<ProcessResponse>('/api/process-urls', { urls });
        return response.data;
    },

    /**
     * Ask a question and get an AI-generated answer.
     */
    async askQuestion(question: string): Promise<AnswerResponse> {
        const response = await api.post<AnswerResponse>('/api/ask', { question });
        return response.data;
    },

    /**
     * Clear all documents from the index.
     */
    async clearIndex(): Promise<{ success: boolean; message: string }> {
        const response = await api.post('/api/clear-index');
        return response.data;
    },
};
