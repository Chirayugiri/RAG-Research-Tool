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
}

export interface AnswerResponse {
    success: boolean;
    answer: string;
    sources: Source[];
}
