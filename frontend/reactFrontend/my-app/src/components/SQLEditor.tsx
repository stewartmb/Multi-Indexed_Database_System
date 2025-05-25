import React, { useState } from 'react';
import CodeMirror from '@uiw/react-codemirror';
import { sql } from '@codemirror/lang-sql';
import { oneDark } from '@codemirror/theme-one-dark'; // tema oscuro legible

interface Props {
    onRun: (query: string) => void;
}

const SQLEditor: React.FC<Props> = ({ onRun }) => {
    const [query, setQuery] = useState('');

    const handleClear = () => setQuery('');

    return (
        <div className="sql-editor-container h-full flex flex-col">
            <div className="sql-editor-header p-2 bg-gray-100">
                <div className="sql-editor-toolbar flex gap-2">
                    <button className="btn-run" onClick={() => onRun(query)}>
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
                            value={query}
                            extensions={[sql()]}
                            onChange={(value) => setQuery(value)}
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
