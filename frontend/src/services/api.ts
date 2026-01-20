/**
 * API service for communicating with the backend.
 */

import axios from 'axios';
import type {
    ProcessResponse,
    AnswerResponse,
    User,
    Token,
    LoginRequest,
    RegisterRequest,
    Chat,
    ChatWithMessages
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add request interceptor to include JWT token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Add response interceptor to handle 401 errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Token expired or invalid
            localStorage.removeItem('auth_token');
            localStorage.removeItem('user');
            window.dispatchEvent(new Event('auth:logout'));
        }
        return Promise.reject(error);
    }
);

export const apiService = {
    // ========== Authentication ==========

    /**
     * Register a new user.
     */
    async register(data: RegisterRequest): Promise<User> {
        const response = await api.post<User>('/api/auth/register', data);
        return response.data;
    },

    /**
     * Login and get access token.
     */
    async login(data: LoginRequest): Promise<Token> {
        const response = await api.post<Token>('/api/auth/login', data);
        return response.data;
    },

    /**
     * Get current user information.
     */
    async getMe(): Promise<User> {
        const response = await api.get<User>('/api/auth/me');
        return response.data;
    },

    // ========== Chat History ==========

    /**
     * Create a new chat session.
     */
    async createChat(title?: string, processed_urls?: string[]): Promise<Chat> {
        const response = await api.post<Chat>('/api/chats', { title, processed_urls });
        return response.data;
    },

    /**
     * Get all user's chats.
     */
    async getChats(limit: number = 50): Promise<Chat[]> {
        const response = await api.get<Chat[]>('/api/chats', { params: { limit } });
        return response.data;
    },

    /**
     * Get a specific chat with messages.
     */
    async getChat(chatId: string): Promise<ChatWithMessages> {
        const response = await api.get<ChatWithMessages>(`/api/chats/${chatId}`);
        return response.data;
    },

    /**
     * Delete a chat session.
     */
    async deleteChat(chatId: string): Promise<{ success: boolean; message: string }> {
        const response = await api.delete(`/api/chats/${chatId}`);
        return response.data;
    },

    // ========== RAG Operations ==========

    /**
     * Process news article URLs.
     */
    async processUrls(urls: string[], chatId?: string): Promise<ProcessResponse> {
        const response = await api.post<ProcessResponse>('/api/process-urls', { urls, chat_id: chatId });
        return response.data;
    },

    /**
     * Ask a question and get an AI-generated answer.
     */
    async askQuestion(question: string, chatId?: string): Promise<AnswerResponse> {
        const response = await api.post<AnswerResponse>('/api/ask', { question, chat_id: chatId });
        return response.data;
    },

    /**
     * Clear user's documents from the index.
     */
    async clearIndex(): Promise<{ success: boolean; message: string }> {
        const response = await api.post('/api/clear-index');
        return response.data;
    },

    /**
     * Get user's processed URLs.
     */
    async getMyUrls(limit: number = 100): Promise<{ success: boolean; urls: any[]; count: number }> {
        const response = await api.get('/api/me/urls', { params: { limit } });
        return response.data;
    },
};

