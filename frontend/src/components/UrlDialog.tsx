import React, { useState } from 'react';
import { MinusCircle, PlusCircle, X, Loader2, Link as LinkIcon } from 'lucide-react';
import { useAppContext } from '../context/AppContext';
import { apiService } from '../services/api';
import './UrlDialog.css';

interface UrlDialogProps {
    isOpen: boolean;
    onClose: () => void;
}

export const UrlDialog: React.FC<UrlDialogProps> = ({ isOpen, onClose }) => {
    const { urls, setUrls, isProcessing, setIsProcessing, setDocumentsProcessed } = useAppContext();
    const [inputValue, setInputValue] = useState('');

    if (!isOpen) return null;

    const handleAddUrl = () => {
        if (!inputValue.trim()) return;

        if (urls.length >= 10) {
            alert('Maximum 10 URLs allowed');
            return;
        }

        try {
            const url = new URL(inputValue); // basic validation
            // Optional: check for duplicates
            if (urls.includes(inputValue)) {
                alert('URL already added');
                return;
            }
            setUrls([...urls, inputValue]);
            setInputValue('');
        } catch (e) {
            alert('Please enter a valid URL including http:// or https://');
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
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
            alert(`✅ ${response.message}\n\nDocuments: ${response.num_documents}\nChunks: ${response.num_chunks}`);
            onClose(); // Optional: close dialog on success
        } catch (error: any) {
            alert(`❌ Failed to process URLs: ${error.response?.data?.detail || error.message}`);
        } finally {
            setIsProcessing(false);
        }
    };

    return (
        <div className="url-dialog-overlay" onClick={onClose}>
            <div className="url-dialog-content" onClick={e => e.stopPropagation()}>
                <div className="url-dialog-header">
                    <div className="header-title-group">
                        <div className="header-icon-box">
                            <LinkIcon size={20} />
                        </div>
                        <div>
                            <h3>Knowledge Sources</h3>
                            <p className="subtitle">Add URLs to the analysis context</p>
                        </div>
                    </div>
                    <button className="close-btn" onClick={onClose}>
                        <X size={20} />
                    </button>
                </div>

                <div className="url-dialog-body">
                    <div className="input-section">
                        <div className="input-wrapper">
                            <input
                                type="url"
                                value={inputValue}
                                onChange={(e) => setInputValue(e.target.value)}
                                onKeyDown={handleKeyDown}
                                placeholder="Paste source URL here..."
                                className="glass-input"
                                disabled={isProcessing || urls.length >= 10}
                                autoFocus
                            />
                            <button
                                onClick={handleAddUrl}
                                disabled={!inputValue || isProcessing || urls.length >= 10}
                                className="add-btn"
                            >
                                <PlusCircle size={20} />
                            </button>
                        </div>
                        <div className="input-status">
                            <span>{urls.length}/10 Sources</span>
                        </div>
                    </div>

                    <div className="url-list-scroll">
                        {urls.length === 0 ? (
                            <div className="empty-state-dialog">
                                <div className="empty-icon-dialog">🌐</div>
                                <p>No sources added yet</p>
                            </div>
                        ) : (
                            <div className="url-list">
                                {urls.map((url, index) => (
                                    <div key={index} className="url-card">
                                        <div className="url-icon">
                                            <div className="status-dot"></div>
                                        </div>
                                        <span className="url-text" title={url}>{url}</span>
                                        <button
                                            onClick={() => removeUrl(index)}
                                            className="card-remove-btn"
                                            disabled={isProcessing}
                                        >
                                            <MinusCircle size={16} />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                <div className="url-dialog-footer">
                    <button
                        onClick={handleProcess}
                        className="process-btn-glow"
                        disabled={isProcessing || urls.length === 0}
                    >
                        {isProcessing ? (
                            <>
                                <Loader2 size={18} className="spinner" />
                                <span>Processing Context...</span>
                            </>
                        ) : (
                            <>
                                <span>Initialize Analysis</span>
                            </>
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
};
