/**
 * Global application context using Context API.
 */

import React, { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import type { Message, User, Chat } from '../types';
import { apiService } from '../services/api';

interface AppContextType {
    // Authentication
    user: User | null;
    isAuthenticated: boolean;
    login: (username: string, password: string) => Promise<void>;
    register: (username: string, email: string, password: string, fullName?: string) => Promise<void>;
    logout: () => void;

    // Messages
    messages: Message[];
    addMessage: (message: Message) => void;
    clearMessages: () => void;

    // URLs
    urls: string[];
    setUrls: (urls: string[]) => void;

    // Chat
    currentChat: Chat | null;
    setCurrentChat: (chat: Chat | null) => void;

    // Loading states
    isProcessing: boolean;
    setIsProcessing: (isProcessing: boolean) => void;
    isLoading: boolean;
    setIsLoading: (isLoading: boolean) => void;
    documentsProcessed: boolean;
    setDocumentsProcessed: (processed: boolean) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [urls, setUrls] = useState<string[]>(['']);
    const [currentChat, setCurrentChat] = useState<Chat | null>(null);
    const [isProcessing, setIsProcessing] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [documentsProcessed, setDocumentsProcessed] = useState(false);

    // Check for existing auth on mount
    useEffect(() => {
        const checkAuth = async () => {
            const token = localStorage.getItem('auth_token');
            const savedUser = localStorage.getItem('user');

            if (token && savedUser) {
                try {
                    // Verify token is still valid
                    const currentUser = await apiService.getMe();
                    setUser(currentUser);
                } catch (error) {
                    // Token invalid, clear storage
                    localStorage.removeItem('auth_token');
                    localStorage.removeItem('user');
                }
            }
        };

        checkAuth();

        // Listen for logout events from API interceptor
        const handleLogout = () => {
            setUser(null);
            setMessages([]);
            setCurrentChat(null);
        };

        window.addEventListener('auth:logout', handleLogout);
        return () => window.removeEventListener('auth:logout', handleLogout);
    }, []);

    const login = async (username: string, password: string) => {
        const tokenResponse = await apiService.login({ username, password });
        localStorage.setItem('auth_token', tokenResponse.access_token);

        const userData = await apiService.getMe();
        setUser(userData);
        localStorage.setItem('user', JSON.stringify(userData));
    };

    const register = async (username: string, email: string, password: string, fullName?: string) => {
        const userData = await apiService.register({
            username,
            email,
            password,
            full_name: fullName
        });

        // Auto-login after registration
        await login(username, password);
    };

    const logout = () => {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
        setUser(null);
        setMessages([]);
        setCurrentChat(null);
        setDocumentsProcessed(false);
    };

    const addMessage = (message: Message) => {
        setMessages((prev) => [...prev, message]);
    };

    const clearMessages = () => {
        setMessages([]);
    };

    return (
        <AppContext.Provider
            value={{
                user,
                isAuthenticated: !!user,
                login,
                register,
                logout,
                messages,
                addMessage,
                clearMessages,
                urls,
                setUrls,
                currentChat,
                setCurrentChat,
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
