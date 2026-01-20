import React, { useState } from 'react';
import { ExternalLink, ChevronDown, ChevronUp } from 'lucide-react';
import type { Source } from '../types';
import './SourceCard.css';

interface SourceCardProps {
    source: Source;
    index: number;
}

export const SourceCard: React.FC<SourceCardProps> = ({ source, index }) => {
    const [isExpanded, setIsExpanded] = useState(false);

    const getDomain = (url: string) => {
        try {
            const domain = new URL(url).hostname;
            return domain.replace('www.', '');
        } catch {
            return 'Unknown source';
        }
    };

    return (
        <div className="source-card">
            <button
                className="source-header"
                onClick={() => setIsExpanded(!isExpanded)}
            >
                <div className="source-info">
                    <span className="source-number">Source {index + 1}</span>
                    <span className="source-domain">{getDomain(source.url)}</span>
                </div>
                {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            </button>

            {isExpanded && (
                <div className="source-content">
                    <p className="source-excerpt">{source.text}</p>
                    <a
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="source-link"
                    >
                        <ExternalLink size={14} />
                        View article
                    </a>
                </div>
            )}
        </div>
    );
};
