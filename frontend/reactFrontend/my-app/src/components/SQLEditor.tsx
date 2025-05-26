import React, { useState, useEffect } from 'react';
import CodeMirror from '@uiw/react-codemirror';
import { sql } from '@codemirror/lang-sql';
import { oneDark } from '@codemirror/theme-one-dark';
import { useQueryUrl } from '../contexts/QueryUrlContext.tsx';

interface Props {
    onRun: (query: string) => void;
    query?: string;
    onQueryChange?: (query: string) => void;
    isLoading?: boolean;
}

const SQLEditor: React.FC<Props> = ({ onRun, query = '', onQueryChange, isLoading = false }) => {
    const [localQuery, setLocalQuery] = useState(query);
    const [tempUrl, setTempUrl] = useState('');
    const { queryUrl, setQueryUrl } = useQueryUrl();

    const updateQueryUrl = (url) => {
        setQueryUrl(url);
    };

    const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setQueryUrl(tempUrl);
    };

    // Update local query when external query changes (from history selection)
    useEffect(() => {
        setLocalQuery(query);
    }, [query]);

    const handleQueryChange = (value: string) => {
        setLocalQuery(value);
        if (onQueryChange) {
            onQueryChange(value);
        }
    };

    const handleClear = () => {
        setLocalQuery('');
        if (onQueryChange) {
            onQueryChange('');
        }
    };

    return (
        <div className="sql-editor-container h-full flex flex-col">
            <div className="sql-editor-header p-3" style={{
                background: 'linear-gradient(145deg, #121212, #1a1a1a)',
                borderBottom: '2px solid #3c3c3c',
                boxShadow: '0 2px 10px rgba(0, 0, 0, 0.3)'
            }}>
                <div className="sql-editor-toolbar flex justify-between items-center">

                    {/* Botones a la izquierda */}
                    <div className="flex gap-3">
                        <button
                            className={`btn-run ${isLoading ? 'btn-run-disabled' : ''}`}
                            onClick={() => onRun(localQuery)}
                            disabled={isLoading || !localQuery.trim()}
                            title={isLoading ? 'Query in progress...' : !localQuery.trim() ? 'Enter a query to run' : 'Run query'}
                        >
                            <span className="mr-2">{isLoading ? '⏳' : '▶'}</span>
                            {isLoading ? 'Running...' : 'Run Query'}
                        </button>

                        <button
                            className={`btn-clear ${isLoading ? 'btn-clear-disabled' : ''}`}
                            onClick={handleClear}
                            disabled={isLoading}
                            title={isLoading ? 'Cannot clear while query is running' : 'Clear editor'}
                        >
                            <span className="mr-2">🗑</span> Clear
                        </button>
                    </div>

                    {/* Campo URL a la derecha */}
                    <form onSubmit={handleSubmit} className="flex items-center gap-3">
                        <input
                            type="text"
                            className="url-input"
                            placeholder="http://127.0.0.1:8085/query"
                            value={tempUrl}
                            onChange={(e) => setTempUrl(e.target.value)}
                        />
                        <button
                            type="submit"
                            className="btn-set-url"
                        >
                            Set URL
                        </button>
                    </form>

                </div>
            </div>

            <div
                className="sql-editor-body flex-1 overflow-auto"
                style={{
                    background: 'linear-gradient(145deg, #0f172a, #1e293b)',
                    scrollbarWidth: 'none',
                    msOverflowStyle: 'none',
                }}
            >
                <style>
                    {`
                    .sql-editor-body::-webkit-scrollbar {
                        width: 8px;
                    }
                    .sql-editor-body::-webkit-scrollbar-track {
                        background: rgba(45, 55, 72, 0.3);
                        border-radius: 4px;
                    }
                    .sql-editor-body::-webkit-scrollbar-thumb {
                        background: linear-gradient(145deg, #374151, #4b5563);
                        border-radius: 4px;
                    }
                    .sql-editor-body::-webkit-scrollbar-thumb:hover {
                        background: linear-gradient(145deg, #4b5563, #6b7280);
                    }
                    
                    .btn-run, .btn-clear, .btn-set-url {
                        padding: 0.75rem 1.5rem;
                        border: none;
                        border-radius: 0.5rem;
                        font-weight: 600;
                        cursor: pointer;
                        transition: all 0.3s ease;
                        position: relative;
                        overflow: hidden;
                        font-size: 0.875rem;
                    }
                    
                    .btn-run, .btn-clear, .btn-set-url {
                        background: linear-gradient(145deg, #374151, #4b5563);
                        color: #e2e8f0;
                        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
                    }
                    
                    .btn-run {
                        background: linear-gradient(145deg, #1e40af, #2563eb);
                    }
                    
                    .btn-run:hover:not(:disabled) {
                        background: linear-gradient(145deg, #2563eb, #3b82f6);
                        transform: translateY(-2px);
                        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.3);
                    }
                    
                    .btn-run:disabled {
                        background: linear-gradient(145deg, #4b5563, #6b7280);
                        cursor: not-allowed;
                        opacity: 0.6;
                        transform: none;
                    }
                    
                    .btn-clear:hover:not(:disabled) {
                        background: linear-gradient(145deg, #4b5563, #6b7280);
                        transform: translateY(-2px);
                        box-shadow: 0 6px 20px rgba(75, 85, 99, 0.3);
                    }
                    
                    .btn-clear:disabled {
                        background: linear-gradient(145deg, #4b5563, #6b7280);
                        cursor: not-allowed;
                        opacity: 0.6;
                        transform: none;
                    }
                    
                    .btn-set-url:hover {
                        background: linear-gradient(145deg, #059669, #10b981);
                        transform: translateY(-2px);
                        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.3);
                    }
                    
                    .btn-set-url {
                        background: linear-gradient(145deg, #047857, #059669);
                    }
                    
                    .url-input {
                        background: linear-gradient(145deg, #374151, #4b5563);
                        color: #e2e8f0;
                        border: 1px solid #6b7280;
                        border-radius: 0.5rem;
                        padding: 0.75rem 1rem;
                        width: 280px;
                        font-size: 0.875rem;
                        transition: all 0.3s ease;
                    }
                    
                    .url-input:focus {
                        outline: none;
                        border-color: #3b82f6;
                        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
                        background: linear-gradient(145deg, #4b5563, #6b7280);
                    }
                    
                    .url-input::placeholder {
                        color: #9ca3af;
                    }
                    
                    /* Hover effects with shimmer */
                    .btn-run::before, .btn-clear::before, .btn-set-url::before {
                        content: '';
                        position: absolute;
                        top: 0;
                        left: -100%;
                        width: 100%;
                        height: 100%;
                        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
                        transition: left 0.5s;
                    }
                    
                    .btn-run:hover::before, .btn-clear:hover::before, .btn-set-url:hover::before {
                        left: 100%;
                    }
                    `}
                </style>

                <CodeMirror 
                    className="sql-editor-body"
                    value={localQuery}
                    extensions={[sql()]}
                    onChange={handleQueryChange}
                    theme={oneDark}
                    placeholder="Write your SQL query here..."
                    basicSetup={{lineNumbers: true}}
                    style={{
                        height: '100%',
                        maxHeight: '100%',
                        overflow: 'scroll',
                        fontFamily: '"JetBrains Mono", "Fira Code", monospace',
                        fontSize: '16px',
                        lineHeight: '1.6',
                    }}
                />
            </div>
        </div>
    );
};

export default SQLEditor;