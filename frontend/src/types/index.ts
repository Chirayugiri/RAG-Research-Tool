/**
 * Type definitions for the RAG News Tool application.
 */

export interface Message {
    id: string;
    type: 'user' | 'ai';
    content: string;
    timestamp: Date;
    sources?: Source[];
}

export interface Source {
    url: string;
    text: string;
}

export interface ProcessResponse {
    success: boolean;
    message: string;
    num_documents: number;
    num_chunks: number;
    new_urls?: number;
    skipped_urls?: number;
    failed_urls?: number;
    skipped_url_list?: string[];
    failed_url_list?: string[];
}

export interface AnswerResponse {
    success: boolean;
    answer: string;
    sources: Source[];
    message_id?: string;
}

// Authentication types
export interface User {
    id: string;
    username: string;
    email: string;
    full_name?: string;
    avatar_url?: string;
    created_at: string;
}

export interface LoginRequest {
    username: string;
    password: string;
}

export interface RegisterRequest {
    username: string;
    email: string;
    password: string;
    full_name?: string;
}

export interface Token {
    access_token: string;
    token_type: string;
}

// Chat types
export interface Chat {
    id: string;
    title: string;
    created_at: string;
    updated_at: string;
    message_count: number;
    processed_urls: string[];
}

export interface ChatWithMessages {
    chat: Chat;
    messages: Message[];
}

