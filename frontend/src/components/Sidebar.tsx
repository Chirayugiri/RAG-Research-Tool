import React, { useState } from 'react';
import { PlusCircle, MinusCircle, Loader2 } from 'lucide-react';
import { useAppContext } from '../context/AppContext';
import { apiService } from '../services/api';
import './Sidebar.css';

export const Sidebar: React.FC = () => {
    const { urls, setUrls, isProcessing, setIsProcessing, setDocumentsProcessed } = useAppContext();
    const [isCollapsed, setIsCollapsed] = useState(false);

    const handleUrlChange = (index: number, value: string) => {
        const newUrls = [...urls];
        newUrls[index] = value;
        setUrls(newUrls);
    };

    const addUrlField = () => {
        if (urls.length < 10) {
            setUrls([...urls, '']);
        }
    };

    const removeUrlField = (index: number) => {
        if (urls.length > 1) {
            const newUrls = urls.filter((_, i) => i !== index);
            setUrls(newUrls);
        }
    };

    const handleProcess = async () => {
        const validUrls = urls.filter(url => url.trim() !== '');

        if (validUrls.length === 0) {
            alert('Please enter at least one URL');
            return;
        }

        setIsProcessing(true);
        try {
            const response = await apiService.processUrls(validUrls);
            setDocumentsProcessed(true);
            alert(`✅ ${response.message}\n\nDocuments: ${response.num_documents}\nChunks: ${response.num_chunks}`);
        } catch (error: any) {
            alert(`❌ Failed to process URLs: ${error.response?.data?.detail || error.message}`);
        } finally {
            setIsProcessing(false);
        }
    };

    return (
        <aside className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
            <div className="sidebar-header">
                <h2 className="sidebar-title">News Articles</h2>
                <button
                    className="collapse-btn"
                    onClick={() => setIsCollapsed(!isCollapsed)}
                >
                    {isCollapsed ? '→' : '←'}
                </button>
            </div>

            {!isCollapsed && (
                <div className="sidebar-content">
                    <p className="sidebar-description">
                        Enter up to 10 news article URLs to analyze
                    </p>

                    <div className="url-list">
                        {urls.map((url, index) => (
                            <div key={index} className="url-input-group">
                                <input
                                    type="url"
                                    value={url}
                                    onChange={(e) => handleUrlChange(index, e.target.value)}
                                    placeholder={`URL ${index + 1}`}
                                    className="url-input"
                                    disabled={isProcessing}
                                />
                                {urls.length > 1 && (
                                    <button
                                        onClick={() => removeUrlField(index)}
                                        className="remove-btn"
                                        disabled={isProcessing}
                                        title="Remove URL"
                                    >
                                        <MinusCircle size={18} />
                                    </button>
                                )}
                            </div>
                        ))}
                    </div>

                    {urls.length < 10 && (
                        <button
                            onClick={addUrlField}
                            className="add-url-btn"
                            disabled={isProcessing}
                        >
                            <PlusCircle size={18} />
                            Add URL
                        </button>
                    )}

                    <button
                        onClick={handleProcess}
                        className="process-btn"
                        disabled={isProcessing}
                    >
                        {isProcessing ? (
                            <>
                                <Loader2 size={18} className="spinner" />
                                Processing...
                            </>
                        ) : (
                            <>
                                🚀 Process URLs
                            </>
                        )}
                    </button>
                </div>
            )}
        </aside>
    );
};
