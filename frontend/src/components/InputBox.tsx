import React, { useState, useRef, useEffect } from 'react';
import { Send } from 'lucide-react';
import { useAppContext } from '../context/AppContext';
import { apiService } from '../services/api';
import './InputBox.css';

export const InputBox: React.FC = () => {
    const [input, setInput] = useState('');
    const textareaRef = useRef<HTMLTextAreaElement>(null);
    const { addMessage, isLoading, setIsLoading, documentsProcessed } = useAppContext();

    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
        }
    }, [input]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!input.trim() || isLoading || !documentsProcessed) return;

        const question = input.trim();
        setInput('');

        // Add user message
        addMessage({
            id: Date.now().toString(),
            type: 'user',
            content: question,
            timestamp: new Date(),
        });

        setIsLoading(true);
        try {
            const response = await apiService.askQuestion(question);

            // Add AI response
            addMessage({
                id: (Date.now() + 1).toString(),
                type: 'ai',
                content: response.answer,
                timestamp: new Date(),
                sources: response.sources,
            });
        } catch (error: any) {
            addMessage({
                id: (Date.now() + 1).toString(),
                type: 'ai',
                content: `❌ Error: ${error.response?.data?.detail || error.message}`,
                timestamp: new Date(),
            });
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    };

    return (
        <div className="input-box-container">
            <form className="input-box" onSubmit={handleSubmit}>
                <textarea
                    ref={textareaRef}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder={
                        documentsProcessed
                            ? 'Ask a question about the news articles...'
                            : 'Process some URLs first to get started'
                    }
                    className="input-textarea"
                    disabled={!documentsProcessed || isLoading}
                    rows={1}
                />
                <button
                    type="submit"
                    className="send-btn"
                    disabled={!input.trim() || isLoading || !documentsProcessed}
                    title="Send message"
                >
                    <Send size={20} />
                </button>
            </form>
        </div>
    );
};
