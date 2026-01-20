import React, { useRef, useEffect } from 'react';
import { useAppContext } from '../context/AppContext';
import { Message } from './Message';
import { LoadingIndicator } from './LoadingIndicator';
import './ChatContainer.css';

export const ChatContainer: React.FC = () => {
    const { messages, isLoading, documentsProcessed } = useAppContext();
    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    return (
        <div className="chat-container">
            {messages.length === 0 && !isLoading ? (
                <div className="empty-state">
                    <div className="empty-icon">💬</div>
                    <h2 className="empty-title">
                        {documentsProcessed ? 'Ask me anything!' : 'Welcome to RAG News Research'}
                    </h2>
                    <p className="empty-description">
                        {documentsProcessed
                            ? 'I\'m ready to answer questions about the news articles you\'ve processed.'
                            : 'Start by adding news article URLs in the sidebar, then ask questions about them.'}
                    </p>
                    {documentsProcessed && (
                        <div className="sample-questions">
                            <p className="sample-title">Try asking:</p>
                            <ul className="sample-list">
                                <li>What are the main topics covered in these articles?</li>
                                <li>Summarize the key findings</li>
                                <li>What are the different perspectives presented?</li>
                            </ul>
                        </div>
                    )}
                </div>
            ) : (
                <div className="messages-list">
                    {messages.map((message) => (
                        <Message key={message.id} message={message} />
                    ))}
                    {isLoading && <LoadingIndicator />}
                    <div ref={messagesEndRef} />
                </div>
            )}
        </div>
    );
};
