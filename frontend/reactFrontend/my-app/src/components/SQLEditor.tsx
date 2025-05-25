import React, { useState } from 'react';

interface Props {
    onRun: (query: string) => void;
}

const SQLEditor: React.FC<Props> = ({ onRun }) => {
    const [query, setQuery] = useState('');

    const handleClear = () => setQuery('');

    return (
        <div className="sql-editor-container">
            <div className="sql-editor-header">
                <div className="sql-editor-toolbar">
                    <button className="btn-run" onClick={() => onRun(query)}>
                        <span className="mr-1">▶</span> Run
                    </button>
                    <button className="btn-clear" onClick={handleClear}>
                        <span className="mr-1">🗑</span> Clear
                    </button>
                    {/*<button className="btn-save">*/}
                    {/*    <span className="mr-1">💾</span> Save*/}
                    {/*</button>*/}
                    {/*<button className="btn-history">*/}
                    {/*    <span className="mr-1">📋</span> History*/}
                    {/*</button>*/}
                </div>
            </div>

            <div className="sql-editor-body">
                <textarea
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    className="sql-textarea"
                    placeholder="Write your SQL query here..."
                />
            </div>
        </div>
    );
};

export default SQLEditor;
