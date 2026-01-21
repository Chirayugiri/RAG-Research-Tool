import React from 'react';
import { Link2, FileText, MessageCircle, Sparkles } from 'lucide-react';
import './WelcomeScreen.css';

export const WelcomeScreen: React.FC = () => {
    return (
        <div className="welcome-screen">
            <div className="welcome-content">
                <h1 className="welcome-title">Welcome to RAG News Research</h1>
                <p className="welcome-subtitle">Cross-article reasoning powered by RAG</p>

                {/* 3-Step Process */}
                <div className="process-steps">
                    <div className="step">
                        <div className="step-number">1</div>
                        <div className="step-icon">
                            <Link2 size={24} />
                        </div>
                        <div className="step-info">
                            <h3>Add</h3>
                            <p>Add 1–5 news article URLs</p>
                        </div>
                    </div>

                    <div className="step-connector"></div>

                    <div className="step">
                        <div className="step-number">2</div>
                        <div className="step-icon extract">
                            <FileText size={24} />
                            <FileText size={20} className="icon-overlay" />
                        </div>
                        <div className="step-info">
                            <h3>We extract & embed</h3>
                            <p>the content</p>
                        </div>
                    </div>

                    <div className="step-connector"></div>

                    <div className="step">
                        <div className="step-number">3</div>
                        <div className="step-icon">
                            <MessageCircle size={24} />
                        </div>
                        <div className="step-info">
                            <h3>Ask deep questions</h3>
                            <p>across sources</p>
                        </div>
                    </div>
                </div>

                {/* Centered Input Field */}
                <div className="welcome-input-container">
                    <div className="welcome-input-wrapper">
                        <Link2 size={20} className="input-icon" />
                        <input
                            type="text"
                            placeholder="Paste a news article URL and press Add Source to get started"
                            className="welcome-input"
                        />
                        <button className="welcome-add-btn">
                            <Sparkles size={18} />
                            Add Source
                        </button>
                    </div>
                </div>

                {/* Suggested Questions */}
                <div className="suggested-questions">
                    <button className="question-chip">
                        💬 What are conflicting claims?
                    </button>
                    <button className="question-chip">
                        📝 Summarize key facts
                    </button>
                    <button className="question-chip">
                        🎯 Who benefits from this news?
                    </button>
                </div>
            </div>
        </div>
    );
};
