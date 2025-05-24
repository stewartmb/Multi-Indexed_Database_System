import React, { useState } from 'react';

interface Props {
    onRun: (query: string) => void;
}

const SQLEditor: React.FC<Props> = ({ onRun }) => {
    const [query, setQuery] = useState('');

    const handleClear = () => setQuery('');

    return (
        <div className="flex flex-col w-full h-full border border-gray-300 rounded shadow bg-white overflow-hidden">
            {/* Encabezado */}
            <div className="flex items-center justify-between px-4 py-2 bg-gray-100 border-b border-gray-300">
                <div className="flex space-x-2">
                    <button
                        className="bg-blue-600 text-white px-3 py-1.5 rounded hover:bg-blue-700 flex items-center shadow"
                        onClick={() => onRun(query)}
                    >
                        <span className="mr-1">▶</span>
                        Run
                    </button>

                    <button
                        className="bg-gray-700 text-white px-3 py-1.5 rounded hover:bg-gray-600 flex items-center shadow"
                        onClick={handleClear}
                    >
                        <span className="mr-1">🗑</span>
                        Clear
                    </button>

                    <button className="bg-green-600 text-white px-3 py-1.5 rounded hover:bg-green-700 flex items-center shadow">
                        <span className="mr-1">💾</span>
                        Save
                    </button>

                    <button className="bg-indigo-600 text-white px-3 py-1.5 rounded hover:bg-indigo-700 flex items-center shadow">
                        <span className="mr-1">📋</span>
                        History
                    </button>
                </div>
            </div>

            {/* Editor */}
            <div className="flex-1 p-3 bg-gray-50 overflow-auto">
                <textarea
                    style={{backgroundColor: '#555555', color: '#f0f0f0'}} // fondo oscuro y texto claro
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    className="w-full h-full p-4 text-base font-mono border border-blue-200 rounded-md resize-none shadow-inner focus:outline-none focus:ring-2 focus:ring-blue-400"
                    placeholder="Write your SQL query here..."
                />

            </div>
        </div>
    );
};

export default SQLEditor;
