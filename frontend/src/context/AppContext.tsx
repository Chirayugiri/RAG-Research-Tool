/**
 * Global application context using Context API.
 */

import React, { createContext, useContext, useState, type ReactNode } from 'react';
import type { Message } from '../types';

interface AppContextType {
    messages: Message[];
    addMessage: (message: Message) => void;
    clearMessages: () => void;
    urls: string[];
    setUrls: (urls: string[]) => void;
    isProcessing: boolean;
    setIsProcessing: (isProcessing: boolean) => void;
    isLoading: boolean;
    setIsLoading: (isLoading: boolean) => void;
    documentsProcessed: boolean;
    setDocumentsProcessed: (processed: boolean) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [urls, setUrls] = useState<string[]>(['']);
    const [isProcessing, setIsProcessing] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [documentsProcessed, setDocumentsProcessed] = useState(false);

    const addMessage = (message: Message) => {
        setMessages((prev) => [...prev, message]);
    };

    const clearMessages = () => {
        setMessages([]);
    };

    return (
        <AppContext.Provider
            value={{
                messages,
                addMessage,
                clearMessages,
                urls,
                setUrls,
                isProcessing,
                setIsProcessing,
                isLoading,
                setIsLoading,
                documentsProcessed,
                setDocumentsProcessed,
            }}
        >
            {children}
        </AppContext.Provider>
    );
};

export const useAppContext = () => {
    const context = useContext(AppContext);
    if (!context) {
        throw new Error('useAppContext must be used within AppProvider');
    }
    return context;
};
