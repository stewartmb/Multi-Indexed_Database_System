import React, { useState } from 'react';
import styles from './Results.module.css'; // Importar los estilos CSS

interface Props {
    data: any[] | null;
    message: string | null;
    error: string | null;
    history: string[];
    columns: string[];
    onSelectHistory?: (query: string) => void;
}

const Results: React.FC<Props> = ({ data, columns, message, error, history, onSelectHistory }) => {
    const [activeTab, setActiveTab] = useState<'data' | 'messages' | 'history'>('data'); // Eliminamos 'explain'

    const [currentPage, setCurrentPage] = useState(1);
    const [inputPage, setInputPage] = useState('');
    const rowsPerPage = 10;

    const startIdx = (currentPage - 1) * rowsPerPage;
    const paginatedData = data ? data.slice(startIdx, startIdx + rowsPerPage) : [];
    const totalPages = data ? Math.ceil(data.length / rowsPerPage) : 1;

    const headers = data && data.length > 0 ? Object.keys(data[0]) : [];

    const handleHistoryClick = (query: string) => {
        if (onSelectHistory) {
            onSelectHistory(query);
        }
    };

    return (
        <div className={styles.general}>
            {/* Tabs */}
            <div className={styles.tabs}>
                {['data', 'messages', 'history'].map((tab) => ( // Eliminamos 'explain'
                    <button
                        key={tab}
                        onClick={() => setActiveTab(tab as any)}
                        className={`${styles.tabButton} ${activeTab === tab ? styles.tabButtonActive : styles.tabButtonInactive} ${activeTab !== tab ? styles.tabButtonHover : ''}`}
                    >
                        {tab === 'data' ? 'Data Output' :
                            tab === 'messages' ? 'Messages' :
                                'History'}
                    </button>
                ))}
            </div>

            {/* Tab Content */}
            <div className={styles.tabContent}>
                {activeTab === 'data' && (
                    <>
                        {error ? (
                            <div className={styles.errorMessage}>Error: {error}</div>
                        ) : data ? (
                            <div className={styles.tableContainer}>
                                <table className={styles.table}>
                                    <thead>
                                    <tr>
                                        {columns.map((columns) => (
                                            <th key={columns}>{columns}</th>
                                        ))}
                                    </tr>
                                    </thead>
                                    <tbody>
                                    {paginatedData.map((row, idx) => (
                                        <tr key={idx}>
                                            {headers.map((header) => (
                                                <td key={header}>{row[header]}</td>
                                            ))}
                                        </tr>
                                    ))}
                                    </tbody>
                                </table>
                                <div className={styles.pagination}>
                                    <button onClick={() => setCurrentPage(1)} disabled={currentPage === 1}>
                                        First
                                    </button>
                                    <button onClick={() => setCurrentPage(p => Math.max(1, p - 1))} disabled={currentPage === 1}>
                                        Previous
                                    </button>
                                    <span>Page {currentPage} of {totalPages}</span>
                                    <button onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))} disabled={currentPage === totalPages}>
                                        Next
                                    </button>
                                    <button onClick={() => setCurrentPage(totalPages)} disabled={currentPage === totalPages}>
                                        Last
                                    </button>
                                    <input
                                        type="number"
                                        min="1"
                                        max={totalPages}
                                        value={inputPage}
                                        onChange={(e) => setInputPage(e.target.value)}
                                        onKeyDown={(e) => {
                                            if (e.key === 'Enter') {
                                                const page = parseInt(inputPage, 10);
                                                if (!isNaN(page) && page >= 1 && page <= totalPages) {
                                                    setCurrentPage(page);
                                                    setInputPage('');
                                                }
                                            }
                                        }}
                                        placeholder="Go to page"
                                        className={styles.pageInput}
                                    />
                                </div>
                            </div>
                        ) : (
                            <div className={styles.noResults}>No results</div>
                        )}
                    </>
                )}

                {activeTab === 'messages' && (
                    <div>
                        {error ? (
                            <div className={styles.errorMessage}>Error: {error}</div>
                        ) : message ? (
                            <div className={styles.infoMessage}>{message}</div>
                        ) : (
                            <p className={styles.infoMessage}>Ready to execute queries.</p>
                        )}
                    </div>
                )}

                {activeTab === 'history' && (
                    <div className={styles.historyList}>
                        {history.length === 0 ? (
                            <p className={styles.infoMessage}>No queries run yet.</p>
                        ) : (
                            <ul style={{ listStyleType: 'none', padding: 0 }}>
                                {history.map((query, idx) => (
                                    <li 
                                        key={idx} 
                                        className={`${styles.historyItem} ${styles.historyItemClickable}`}
                                        onClick={() => handleHistoryClick(query)}
                                        title="Click to copy to SQL editor"
                                    >
                                        <code>{query}</code>
                                    </li>
                                ))}
                            </ul>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default Results;