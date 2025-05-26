import React, { useState } from 'react';
import styles from '../../styles/Results.module.css'; // Importar los estilos CSS

interface Props {
    data: any[] | null;
    message: string | null;
    error: string | null;
    history: string[];
    columns: string[];
    onSelectHistory?: (query: string) => void;
    isLoading?: boolean;
}

const Results: React.FC<Props> = ({ data, columns, message, error, history, onSelectHistory, isLoading = false }) => {
    const [activeTab, setActiveTab] = useState<'data' | 'messages' | 'history'>('data'); // Eliminamos 'explain'

    const [currentPage, setCurrentPage] = useState(1);
    const [inputPage, setInputPage] = useState('');
    const rowsPerPage = 10;

    const startIdx = (currentPage - 1) * rowsPerPage;
    const paginatedData = data ? data.slice(startIdx, startIdx + rowsPerPage) : [];
    const totalPages = data ? Math.ceil(data.length / rowsPerPage) : 1;

    // Debug logging
    React.useEffect(() => {
        console.log('Results component received:', {
            data,
            columns,
            paginatedData,
            currentPage,
            totalPages
        });
    }, [data, columns, paginatedData, currentPage, totalPages]);

    const headers = data && data.length > 0 ? Object.keys(data[0]) : [];

    const handleHistoryClick = (query: string) => {
        // Prevent history selection while loading
        if (isLoading) {
            return;
        }
        if (onSelectHistory) {
            onSelectHistory(query);
        }
    };

    // Function to safely render cell content
    const renderCellContent = (row: any, column: string) => {
        console.log('Rendering cell:', { column, rowData: row, value: row[column] });
        const value = row[column];
        
        if (value === null || value === undefined) {
            return 'NULL';
        }
        if (typeof value === 'object') {
            return JSON.stringify(value);
        }
        return String(value);
    };

    // Debug logging for data changes
    React.useEffect(() => {
        if (data && data.length > 0) {
            console.log('Sample data row:', data[0]);
            console.log('Available columns:', columns);
            console.log('Column values in first row:', 
                columns.map(col => ({ 
                    column: col, 
                    value: data[0][col],
                    type: typeof data[0][col]
                }))
            );
        }
    }, [data, columns]);

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
                        {isLoading ? (
                            <div className={styles.loadingMessage}>
                                <div className={styles.spinner}></div>
                                <span>Executing query...</span>
                            </div>
                        ) : error ? (
                            <div className={styles.errorMessage}>Error: {error}</div>
                        ) : data && data.length > 0 ? (
                            <div className={styles.tableContainer}>
                                <table className={styles.table}>
                                    <thead>
                                    <tr>
                                        {columns.map((column, index) => (
                                            <th key={`${column}-${index}`} title={column}>
                                                {column}
                                            </th>
                                        ))}
                                    </tr>
                                    </thead>
                                    <tbody>
                                    {paginatedData.map((row, rowIdx) => {
                                        console.log(`Row ${rowIdx} data:`, row);
                                        return (
                                            <tr key={rowIdx}>
                                                {columns.map((column, colIdx) => (
                                                    <td key={`${rowIdx}-${colIdx}`} title={String(row[column])}>
                                                        {renderCellContent(row, column)}
                                                    </td>
                                                ))}
                                            </tr>
                                        );
                                    })}
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
                            <div className={styles.noResults}>
                                {data === null ? 'Run a query to see results' : 'No results to display'}
                            </div>
                        )}
                    </>
                )}

                {activeTab === 'messages' && (
                    <div>
                        {isLoading ? (
                            <div className={styles.loadingMessage}>
                                <div className={styles.spinner}></div>
                                <span>Executing query...</span>
                            </div>
                        ) : error ? (
                            <div className={styles.errorMessage}>{"Error: \n" + error}</div>
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
                                        className={`${styles.historyItem} ${!isLoading ? styles.historyItemClickable : styles.historyItemDisabled}`}
                                        onClick={() => handleHistoryClick(query)}
                                        title={isLoading ? "Cannot select while query is running" : "Click to copy to SQL editor"}
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