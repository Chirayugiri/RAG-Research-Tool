import React, { useRef, useEffect } from 'react';
import { useAppContext } from '../context/AppContext';
import { Message } from './Message';
import { LoadingIndicator } from './LoadingIndicator';
import { WelcomeScreen } from './WelcomeScreen';
import './ChatContainer.css';

export const ChatContainer: React.FC = () => {
    const { messages, isLoading } = useAppContext();
    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    return (
        <div className="chat-container">
            {messages.length === 0 && !isLoading ? (
                <WelcomeScreen />
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
