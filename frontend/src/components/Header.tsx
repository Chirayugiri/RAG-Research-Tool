import React, { useState } from 'react';
import { Moon, Sun, Trash2, LogOut, Sparkles } from 'lucide-react';
import { apiService } from '../services/api';
import { useAppContext } from '../context/AppContext';
import './Header.css';

export const Header: React.FC = () => {
    const [theme, setTheme] = useState<'light' | 'dark'>('light');
    const { user, logout, clearMessages, setDocumentsProcessed } = useAppContext();

    const toggleTheme = () => {
        const newTheme = theme === 'light' ? 'dark' : 'light';
        setTheme(newTheme);
        document.documentElement.setAttribute('data-theme', newTheme);
    };

    const handleClearIndex = async () => {
        if (!confirm('Are you sure you want to clear your documents? This will remove all processed articles from your knowledge base.')) {
            return;
        }

        try {
            await apiService.clearIndex();
            clearMessages();
            setDocumentsProcessed(false);
            alert('Your documents have been cleared successfully!');
        } catch (error) {
            alert('Failed to clear documents');
            console.error(error);
        }
    };

    const handleLogout = () => {
        if (confirm('Are you sure you want to logout?')) {
            logout();
        }
    };

    return (
        <header className="header">
            <div className="header-content">
                <div className="header-left">
                    <div className="logo">
                        <div className="logo-icon">
                            <Sparkles size={22} strokeWidth={2.5} />
                        </div>
                        <h1 className="logo-text">Research Bot</h1>
                    </div>
                </div>

                <div className="header-right">
                    <div className="user-info">
                        <span className="username">{user?.username}</span>
                    </div>

                    <button
                        className="icon-btn"
                        onClick={handleClearIndex}
                        title="Clear My Documents"
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

                    <button
                        className="icon-btn logout-btn"
                        onClick={handleLogout}
                        title="Logout"
                    >
                        <LogOut size={20} />
                    </button>
                </div>
            </div>
        </header>
    );
};

