import React, { useState } from 'react';
import { Moon, Sun, Trash2 } from 'lucide-react';
import { apiService } from '../services/api';
import { useAppContext } from '../context/AppContext';
import './Header.css';

export const Header: React.FC = () => {
    const [theme, setTheme] = useState<'light' | 'dark'>('light');
    const { clearMessages, setDocumentsProcessed } = useAppContext();

    const toggleTheme = () => {
        const newTheme = theme === 'light' ? 'dark' : 'light';
        setTheme(newTheme);
        document.documentElement.setAttribute('data-theme', newTheme);
    };

    const handleClearIndex = async () => {
        if (!confirm('Are you sure you want to clear all documents?')) {
            return;
        }

        try {
            await apiService.clearIndex();
            clearMessages();
            setDocumentsProcessed(false);
            alert('Index cleared successfully!');
        } catch (error) {
            alert('Failed to clear index');
            console.error(error);
        }
    };

    return (
        <header className="header">
            <div className="header-content">
                <div className="header-left">
                    <div className="logo">
                        <span className="logo-icon">📰</span>
                        <h1 className="logo-text">RAG News Research</h1>
                    </div>
                </div>

                <div className="header-right">
                    <button
                        className="icon-btn"
                        onClick={handleClearIndex}
                        title="Clear Index"
                    >
                        <Trash2 size={20} />
                    </button>

                    <button
                        className="icon-btn"
                        onClick={toggleTheme}
                        title="Toggle Theme"
                    >
                        {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
                    </button>
                </div>
            </div>
        </header>
    );
};
