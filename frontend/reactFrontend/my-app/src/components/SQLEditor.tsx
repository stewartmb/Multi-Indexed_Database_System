import React, { useState } from 'react';

interface Props {
    onRun: (query: string) => void;
}

const SQLEditor: React.FC<Props> = ({ onRun }) => {
    const [query, setQuery] = useState('');

    const handleClear = () => setQuery('');

    return (
        <div className="p-4 border-b border-gray-300">
            {/* Toolbar */}
            <div className="flex items-center mb-3 space-x-2">
                <button
                    className="bg-blue-600 text-white px-3 py-1.5 rounded hover:bg-blue-700 flex items-center"
                    onClick={() => onRun(query)}
                >
                    <span className="mr-1">▶</span>
                    Run
                </button>

                <div className="w-px h-6 bg-gray-400 mx-2" />

                <button
                    className="bg-gray-700 text-white px-3 py-1.5 rounded hover:bg-gray-600 flex items-center"
                    onClick={handleClear}
                >
                    <span className="mr-1">🗑</span>
                    Clear
                </button>

                <button className="bg-gray-700 text-white px-3 py-1.5 rounded hover:bg-gray-600 flex items-center">
                    <span className="mr-1">💾</span>
                    Save
                </button>

                <button className="bg-gray-700 text-white px-3 py-1.5 rounded hover:bg-gray-600 flex items-center">
                    <span className="mr-1">📋</span>
                    History
                </button>
            </div>

            {/* Editor */}
            <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full h-40 p-2 font-mono border border-gray-300 rounded resize-none"
                placeholder="Write your SQL query here..."
            />
        </div>
    );
};

export default SQLEditor;
