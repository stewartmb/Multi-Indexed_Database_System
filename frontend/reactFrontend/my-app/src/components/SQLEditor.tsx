import React, { useState, useEffect } from 'react';
import CodeMirror from '@uiw/react-codemirror';
import { sql } from '@codemirror/lang-sql';
import { EditorView } from '@codemirror/view';
import { HighlightStyle, syntaxHighlighting } from '@codemirror/language';
import { tags as t } from '@lezer/highlight';
import { useQueryUrl } from '../contexts/QueryUrlContext.tsx';

interface Props {
    onRun: (query: string) => void;
    query?: string;
    onQueryChange?: (query: string) => void;
    isLoading?: boolean;
}

// Define custom syntax highlighting based on the parser grammar
const myHighlightStyle = HighlightStyle.define([
    // Keywords from parser
    { tag: t.keyword, color: "#60a5fa" },           // create, select, insert, delete, where, from, etc.
    { tag: t.atom, color: "#38bdf8" },              // int, float, double, varchar, etc.
    { tag: t.string, color: "#4ade80" },            // String literals
    { tag: t.number, color: "#f87171" },            // Numbers
    { tag: t.operator, color: "#94a3b8" },          // ==, !=, <, >, <=, >=
    { tag: t.keyword, color: "#c084fc" },           // primary key
    { tag: t.variableName, color: "#e879f9" },      // column names
    { tag: t.name, color: "#38bdf8" },              // table names
    { tag: t.comment, color: "#64748b", fontStyle: "italic" }, // Comments
    { tag: t.atom, color: "#fb923c" },              // closest, between, and special keywords
    { tag: t.atom, color: "#a78bfa" },              // rtree, bptree, seq, isam, hash
    { tag: t.punctuation, color: "#cbd5e1" },       // ( ) , ;
]);

// Define custom theme
const myTheme = EditorView.theme({
    "&": {
        backgroundColor: "#1e1e1e",
        color: "#e2e8f0",
        height: "100%"
    },
    ".cm-content": {
        fontFamily: "'JetBrains Mono', monospace",
        padding: "0.5rem 0"
    },
    ".cm-line": {
        padding: "0 1rem"
    },
    ".cm-gutters": {
        backgroundColor: "#1e1e1e",
        border: "none",
        borderRight: "1px solid #2d3748",
        color: "#4a5568"
    },
    ".cm-activeLineGutter, .cm-activeLine": {
        backgroundColor: "rgba(30, 41, 59, 0.5)"
    },
    ".cm-selectionBackground": {
        backgroundColor: "rgba(147, 51, 234, 0.35) !important"
    },
    ".cm-cursor": {
        borderLeft: "2px solid #94a3b8"
    },
    "&.cm-focused .cm-selectionBackground": {
        backgroundColor: "rgba(147, 51, 234, 0.45) !important"
    },
    "&.cm-focused .cm-cursor": {
        borderLeftColor: "#e2e8f0"
    }
});

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
            <div className="sql-editor-header" style={{
                padding: '0.5rem',
                background: '#1e1e1e',
                borderBottom: '1px solid #2d3748'
            }}>
                <div className="flex items-center gap-2">
                    <button
                        className="editor-btn"
                        onClick={() => onRun(localQuery)}
                        disabled={isLoading || !localQuery.trim()}
                        title={isLoading ? 'Query in progress...' : !localQuery.trim() ? 'Enter a query to run' : 'Run query'}
                    >
                        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            {isLoading ? (
                                <path d="M6 12h12M12 6v12" />
                            ) : (
                                <path d="M5 3l14 9-14 9V3z" />
                            )}
                        </svg>
                    </button>

                    <button
                        className="editor-btn"
                        onClick={handleClear}
                        disabled={isLoading}
                        title="Clear editor"
                    >
                        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3-3h6M9 3v3M15 3v3M4 6h16" />
                        </svg>
                    </button>
                </div>
            </div>

            <div className="sql-editor-body flex-1" style={{ background: '#1e1e1e' }}>
                <style>
                    {`
                    .editor-btn {
                        display: inline-flex;
                        align-items: center;
                        justify-content: center;
                        width: 2rem;
                        height: 2rem;
                        padding: 0.4rem;
                        border: none;
                        border-radius: 0.25rem;
                        background: transparent;
                        color: #94a3b8;
                        transition: all 0.15s ease;
                    }
                    
                    .editor-btn:hover:not(:disabled) {
                        background: #2d3748;
                        color: #e2e8f0;
                    }
                    
                    .editor-btn:disabled {
                        opacity: 0.5;
                        cursor: not-allowed;
                    }

                    .editor-btn svg {
                        transition: transform 0.15s ease;
                    }

                    .editor-btn:hover:not(:disabled) svg {
                        transform: scale(1.1);
                    }

                    /* SQL Editor Styles */
                    .cm-editor {
                        background: #1e1e1e !important;
                        color: #e2e8f0 !important;
                    }

                    .cm-editor .cm-content {
                        font-family: 'JetBrains Mono', monospace;
                        padding: 0.5rem 0;
                    }

                    .cm-editor .cm-line {
                        padding: 0 1rem;
                    }

                    .cm-editor .cm-gutters {
                        background: #1e1e1e !important;
                        border-right: 1px solid #2d3748;
                        color: #4a5568;
                    }

                    .cm-editor .cm-activeLineGutter,
                    .cm-editor .cm-activeLine {
                        background: rgba(30, 41, 59, 0.5) !important;
                    }

                    .cm-editor .cm-cursor {
                        border-left: 2px solid #94a3b8;
                    }

                    .cm-editor .cm-selectionBackground {
                        background: rgba(147, 51, 234, 0.35) !important;
                    }

                    /* SQL Syntax Highlighting */
                    .cm-editor .cm-keyword {
                        color: #60a5fa !important; /* SELECT, FROM, WHERE */
                    }

                    .cm-editor .cm-operator {
                        color: #94a3b8 !important; /* =, <, > */
                    }

                    .cm-editor .cm-number {
                        color: #f87171 !important; /* Numbers */
                    }

                    .cm-editor .cm-string {
                        color: #4ade80 !important; /* String literals */
                    }

                    .cm-editor .cm-comment {
                        color: #64748b !important;
                        font-style: italic;
                    }

                    .cm-editor .cm-def {
                        color: #38bdf8 !important; /* Table names */
                    }

                    .cm-editor .cm-variable {
                        color: #e879f9 !important; /* Column names */
                    }

                    .cm-editor .cm-punctuation {
                        color: #cbd5e1 !important;
                    }

                    .cm-editor .cm-property {
                        color: #a78bfa !important;
                    }
                    `}
                </style>

                <CodeMirror 
                    value={localQuery}
                    height="100%"
                    extensions={[
                        sql(),
                        syntaxHighlighting(myHighlightStyle),
                        myTheme
                    ]}
                    onChange={handleQueryChange}
                    placeholder="Write your SQL query here..."
                    style={{
                        fontSize: '14px',
                        height: '100%'
                    }}
                />
            </div>
        </div>
    );
};

export default SQLEditor;