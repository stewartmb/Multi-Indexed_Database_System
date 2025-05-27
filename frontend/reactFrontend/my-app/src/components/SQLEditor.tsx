import React, { useState, useEffect } from 'react';
import CodeMirror from '@uiw/react-codemirror';
import { sql } from '@codemirror/lang-sql';
import { EditorView } from '@codemirror/view';
import { HighlightStyle, syntaxHighlighting } from '@codemirror/language';
import { tags as t } from '@lezer/highlight';
import { useQueryUrl } from '../contexts/QueryUrlContext.tsx';
import {completeFromList} from "@codemirror/autocomplete";

import '../styles/SQLEditor.css';






interface Props {
    onRun: (query: string) => void;
    query?: string;
    onQueryChange?: (query: string) => void;
    isLoading?: boolean;
}

// Define custom syntax highlighting based on the parser grammar
const myHighlightStyle = HighlightStyle.define([
    // Keywords from parser t.atom
    { tag: t.keyword, color: "#9d9af5" },           // create, select, insert, delete, where, from, etc.
    { tag: t.typeName, color: "#38bdf8" },              // int, float, double, varchar, etc.
    { tag: t.string, color: "#4ade80" },            // String literals        
    { tag: t.number, color: "#00ffff" },            // Numbers
    { tag: t.operator, color: "#dbd1c5" },          // ==, !=, <, >, <=, >=
    { tag: t.variableName, color: "#e879f9" },      // column names
    { tag: t.name, color: "#7ec1de" },              // table names
    { tag: t.comment, color: "#64748b", fontStyle: "italic" }, // Comments
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
        backgroundColor: "rgba(70, 70, 70, 0.55) !important"
    },
    ".cm-cursor": {
        borderLeft: "2px solid #94a3b8"
    },
    "&.cm-focused .cm-selectionBackground": {
        backgroundColor: "rgba(15, 99, 138, 0.62) !important"
    },
    "&.cm-focused .cm-cursor": {
        borderLeftColor: "#e2e8f0"
    },
    "&.cm-keyword": {
        color: "#000000"
    },
});

const SQLEditor: React.FC<Props> = ({ onRun, query = '', onQueryChange, isLoading = false }) => {
    const [localQuery, setLocalQuery] = useState(query);
    const [tempUrl, setTempUrl] = useState('');
    const { queryUrl, setQueryUrl } = useQueryUrl();

    const updateQueryUrl = (url: string) => {
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