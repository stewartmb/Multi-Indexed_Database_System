import React, { useState, useEffect } from 'react';
import CodeMirror from '@uiw/react-codemirror';
import { sql } from '@codemirror/lang-sql';
import { oneDark } from '@codemirror/theme-one-dark'; // tema oscuro legible

interface Props {
    onRun: (query: string) => void;
    query?: string;
    onQueryChange?: (query: string) => void;
}

const SQLEditor: React.FC<Props> = ({ onRun, query = '', onQueryChange }) => {
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
                    <button className="btn-run" onClick={() => onRun(localQuery)}>
                        <span className="mr-1">▶</span> Run
                    </button>
                    <button className="btn-clear" onClick={handleClear}>
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