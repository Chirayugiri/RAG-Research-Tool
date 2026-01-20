import React from 'react';
import ReactMarkdown from 'react-markdown';
import { User, Bot } from 'lucide-react';
import type { Message as MessageType } from '../types';
import { SourceCard } from './SourceCard';
import './Message.css';

interface MessageProps {
    message: MessageType;
}

export const Message: React.FC<MessageProps> = ({ message }) => {
    const isUser = message.type === 'user';

    const formatTime = (date: Date) => {
        return new Date(date).toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
        });
    };

    return (
        <div className={`message ${isUser ? 'message-user' : 'message-ai'}`}>
            <div className="message-avatar">
                {isUser ? <User size={20} /> : <Bot size={20} />}
            </div>

            <div className="message-content-wrapper">
                <div className="message-bubble">
                    <ReactMarkdown>{message.content}</ReactMarkdown>
                </div>

                {!isUser && message.sources && message.sources.length > 0 && (
                    <div className="message-sources">
                        <p className="sources-title">Sources:</p>
                        <div className="sources-list">
                            {message.sources.map((source, index) => (
                                <SourceCard key={index} source={source} index={index} />
                            ))}
                        </div>
                    </div>
                )}

                <span className="message-time">{formatTime(message.timestamp)}</span>
            </div>
        </div>
    );
};
