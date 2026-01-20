import React from 'react';
import './LoadingIndicator.css';

export const LoadingIndicator: React.FC = () => {
    return (
        <div className="loading-indicator">
            <div className="loading-avatar">
                <span className="loading-icon">🤖</span>
            </div>
            <div className="loading-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    );
};
