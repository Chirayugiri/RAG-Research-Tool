import React, { useState, useRef, useEffect } from 'react';
import { Sparkles, Link2, History, Settings, X, Plus, Trash2, Loader2 } from 'lucide-react';
import { useAppContext } from '../context/AppContext';
import { apiService } from '../services/api';
import './Sidebar.css';

interface UrlModalProps {
    isOpen: boolean;
    onClose: () => void;
}

const UrlModal: React.FC<UrlModalProps> = ({ isOpen, onClose }) => {
    const { urls, setUrls, isProcessing, setIsProcessing, setDocumentsProcessed } = useAppContext();
    const [inputValue, setInputValue] = useState('');
    const inputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        if (isOpen && inputRef.current) {
            setTimeout(() => inputRef.current?.focus(), 100);
        }
    }, [isOpen]);

    const handleAddUrl = () => {
        if (!inputValue.trim()) return;

        if (urls.length >= 10) {
            alert('Maximum 10 URLs allowed');
            return;
        }

        try {
            new URL(inputValue);
            setUrls([...urls, inputValue]);
            setInputValue('');
        } catch (e) {
            alert('Please enter a valid URL');
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') {
            handleAddUrl();
        }
    };

    const removeUrl = (index: number) => {
        const newUrls = urls.filter((_, i) => i !== index);
        setUrls(newUrls);
    };

    const handleProcess = async () => {
        if (urls.length === 0) {
            alert('Please add at least one URL');
            return;
        }

        setIsProcessing(true);
        try {
            const response = await apiService.processUrls(urls);
            setDocumentsProcessed(true);
            onClose();
            alert(`✅ ${response.message}\n\nDocuments: ${response.num_documents}\nChunks: ${response.num_chunks}`);
        } catch (error: any) {
            alert(`❌ Failed to process URLs: ${error.response?.data?.detail || error.message}`);
        } finally {
            setIsProcessing(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="url-modal" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h3>Manage Sources</h3>
                    <button className="modal-close-btn" onClick={onClose}>
                        <X size={20} />
                    </button>
                </div>

                <div className="modal-body">
                    <div className="url-input-section">
                        <input
                            ref={inputRef}
                            type="url"
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onKeyPress={handleKeyPress}
                            placeholder="Paste article URL..."
                            className="modal-url-input"
                            disabled={isProcessing}
                        />
                        <button
                            onClick={handleAddUrl}
                            disabled={!inputValue || isProcessing}
                            className="modal-add-btn"
                        >
                            <Plus size={20} />
                        </button>
                    </div>

                    <div className="url-list-container">
                        {urls.length === 0 ? (
                            <div className="empty-state">
                                <Link2 size={40} className="empty-icon" />
                                <p>No sources added yet</p>
                                <span className="empty-hint">Add URLs to get started</span>
                            </div>
                        ) : (
                            <div className="url-items">
                                {urls.map((url, index) => (
                                    <div key={index} className="url-item">
                                        <div className="url-item-content">
                                            <Link2 size={16} className="url-icon" />
                                            <span className="url-text">{url}</span>
                                        </div>
                                        <button
                                            onClick={() => removeUrl(index)}
                                            className="url-delete-btn"
                                            disabled={isProcessing}
                                        >
                                            <Trash2 size={16} />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                <div className="modal-footer">
                    <div className="url-count">
                        {urls.length} / 10 sources
                    </div>
                    <button
                        onClick={handleProcess}
                        disabled={isProcessing || urls.length === 0}
                        className="process-modal-btn"
                    >
                        {isProcessing ? (
                            <>
                                <Loader2 size={18} className="spinner" />
                                Processing...
                            </>
                        ) : (
                            <>
                                <Sparkles size={18} />
                                Process Sources
                            </>
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
};

export const Sidebar: React.FC = () => {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const { urls } = useAppContext();

    return (
        <>
            <aside className="perplexity-sidebar">
                <div className="sidebar-top">
                    <div className="sidebar-logo">
                        <Sparkles size={24} strokeWidth={2} />
                    </div>

                    <nav className="sidebar-nav">
                        <button
                            className="nav-btn"
                            title="Add Sources"
                            onClick={() => setIsModalOpen(true)}
                        >
                            <Link2 size={20} />
                            <span className="nav-label">Sources</span>
                            {urls.length > 0 && <span className="badge">{urls.length}</span>}
                        </button>

                        <button className="nav-btn" title="History">
                            <History size={20} />
                            <span className="nav-label">History</span>
                        </button>
                    </nav>
                </div>

                <div className="sidebar-bottom">
                    <button className="nav-btn" title="Settings">
                        <Settings size={20} />
                        <span className="nav-label">Settings</span>
                    </button>
                </div>
            </aside>

            <UrlModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
        </>
    );
};
