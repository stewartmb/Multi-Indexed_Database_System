import React, { useState } from 'react';

interface Props {
    data: any[] | null;
    error: string | null;
}

const Results: React.FC<Props> = ({ data, error }) => {
    const [activeTab, setActiveTab] = useState<'data' | 'messages' | 'explain' | 'history'>('data');

    const headers = data && data.length > 0 ? Object.keys(data[0]) : [];

    return (
        <div className="h-full flex flex-col border-t border-gray-300">
            {/* Tabs */}
            <div className="flex border-b border-gray-300 bg-gray-100">
                {['data', 'messages', 'explain', 'history'].map((tab) => (
                    <button
                        key={tab}
                        onClick={() => setActiveTab(tab as any)}
                        className={`px-4 py-2 text-sm capitalize ${
                            activeTab === tab
                                ? 'border-b-2 border-blue-500 text-blue-600'
                                : 'text-gray-600 hover:text-black'
                        }`}
                    >
                        {tab === 'data' ? 'Data Output' :
                            tab === 'messages' ? 'Messages' :
                                tab === 'explain' ? 'Query Plan' :
                                    'History'}
                    </button>
                ))}
            </div>

            {/* Tab Content */}
            <div className="flex-1 overflow-auto p-4 text-sm">
                {activeTab === 'data' && (
                    <>
                        {error ? (
                            <div className="text-red-600">Error: {error}</div>
                        ) : data ? (
                            <table className="w-full table-auto border-collapse">
                                <thead>
                                <tr>
                                    {headers.map((header) => (
                                        <th key={header} className="border px-2 py-1 bg-gray-100 text-left">{header}</th>
                                    ))}
                                </tr>
                                </thead>
                                <tbody>
                                {data.map((row, idx) => (
                                    <tr key={idx}>
                                        {headers.map((header) => (
                                            <td key={header} className="border px-2 py-1">{row[header]}</td>
                                        ))}
                                    </tr>
                                ))}
                                </tbody>
                            </table>
                        ) : (
                            <div className="text-gray-500">No results</div>
                        )}
                    </>
                )}

                {activeTab === 'messages' && (
                    <div>
                        <p>Ready to execute queries.</p>
                        {error && (
                            <div className="mt-2 text-red-600">Error: {error}</div>
                        )}
                    </div>
                )}

                {activeTab === 'explain' && (
                    <div className="text-gray-500 italic">
                        Query plan will appear here after running <code>EXPLAIN</code>
                    </div>
                )}

                {activeTab === 'history' && (
                    <div className="text-gray-500 italic">
                        Query history will appear here
                    </div>
                )}
            </div>
        </div>
    );
};

export default Results;
