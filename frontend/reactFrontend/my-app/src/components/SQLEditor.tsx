import React, { useState, useEffect } from 'react';
import CodeMirror from '@uiw/react-codemirror';
import { sql } from '@codemirror/lang-sql';
import { oneDark } from '@codemirror/theme-one-dark'; // tema oscuro legible

interface Props {
    onRun: (query: string) => void;
    query?: string;
    onQueryChange?: (query: string) => void;
    isLoading?: boolean;
}

const SQLEditor: React.FC<Props> = ({ onRun, query = '', onQueryChange, isLoading = false }) => {
    const [localQuery, setLocalQuery] = useState(query);

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
            <div className="sql-editor-header p-2 bg-gray-100">
                <div className="sql-editor-toolbar flex gap-2">
                    <button 
                        className={`btn-run ${isLoading ? 'btn-run-disabled' : ''}`} 
                        onClick={() => onRun(localQuery)}
                        disabled={isLoading || !localQuery.trim()}
                        title={isLoading ? 'Query in progress...' : !localQuery.trim() ? 'Enter a query to run' : 'Run query'}
                    >
                        <span className="mr-1">{isLoading ? '⏳' : '▶'}</span> 
                        {isLoading ? 'Running...' : 'Run'}
                    </button>
                    <button 
                        className={`btn-clear ${isLoading ? 'btn-clear-disabled' : ''}`} 
                        onClick={handleClear}
                        disabled={isLoading}
                        title={isLoading ? 'Cannot clear while query is running' : 'Clear editor'}
                    >
                        <span className="mr-1">🗑</span> Clear
                    </button>
                </div>
            </div>

            <div
                className="sql-editor-body flex-1 overflow-auto"
                style={{
                    backgroundColor: '#282c34',
                    scrollbarWidth: 'none',        // Firefox
                    msOverflowStyle: 'none',       // IE/Edge
                }}
            >
                <style>
                    {`
                    .sql-editor-body::-webkit-scrollbar {
                        display: none;
                    }
                    .btn-run, .btn-clear {
                        padding: 8px 16px;
                        border: none;
                        border-radius: 4px;
                        font-weight: 500;
                        cursor: pointer;
                        transition: all 0.2s ease;
                    }
                    .btn-run {
                        background-color: #3b82f6;
                        color: white;
                    }
                    .btn-run:hover:not(:disabled) {
                        background-color: #2563eb;
                    }
                    .btn-run:disabled {
                        background-color: #9ca3af;
                        cursor: not-allowed;
                        opacity: 0.6;
                    }
                    .btn-clear {
                        background-color: #6b7280;
                        color: white;
                    }
                    .btn-clear:hover:not(:disabled) {
                        background-color: #4b5563;
                    }
                    .btn-clear:disabled {
                        background-color: #9ca3af;
                        cursor: not-allowed;
                        opacity: 0.6;
                    }
                    `}
                </style>

                <CodeMirror className={"sql-editor-body"}
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
                                fontFamily: '"Fira Code", monospace',
                                fontSize: '20px',
                                lineHeight: '1.6',
                            }}
                />
            </div>
        </div>
    );
};

export default SQLEditor;