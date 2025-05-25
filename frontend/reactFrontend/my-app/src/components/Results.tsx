import React, { useState } from 'react';
import styles from './Results.module.css'; // Importar los estilos CSS

interface Props {
    data: any[] | null;
    error: string | null;
    history: string[];
}

const Results: React.FC<Props> = ({ data, error, history }) => {
    const [activeTab, setActiveTab] = useState<'data' | 'messages' | 'explain' | 'history'>('data');

    const headers = data && data.length > 0 ? Object.keys(data[0]) : [];

    return (
        <div className="h-full flex flex-col border-t border-gray-300">
            {/* Tabs */}
            <div className={styles.tabs}>
                {['data', 'messages', 'explain', 'history'].map((tab) => (
                    <button
                        key={tab}
                        onClick={() => setActiveTab(tab as any)}
                        className={`${styles.tabButton} ${activeTab === tab ? styles.tabButtonActive : styles.tabButtonInactive} ${activeTab !== tab ? styles.tabButtonHover : ''}`}
                    >
                        {tab === 'data' ? 'Data Output' :
                            tab === 'messages' ? 'Messages' :
                                tab === 'explain' ? 'Query Plan' :
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
                                        {headers.map((header) => (
                                            <th key={header}>{header}</th>
                                        ))}
                                    </tr>
                                    </thead>
                                    <tbody>
                                    {data.map((row, idx) => (
                                        <tr key={idx}>
                                            {headers.map((header) => (
                                                <td key={header}>{row[header]}</td>
                                            ))}
                                        </tr>
                                    ))}
                                    </tbody>
                                </table>
                            </div>
                        ) : (
                            <div className={styles.noResults}>No results</div>
                        )}
                    </>
                )}

                {activeTab === 'messages' && (
                    <div>
                        <p>Ready to execute queries.</p>
                        {error && (
                            <div className={styles.errorMessage}>Error: {error}</div>
                        )}
                    </div>
                )}

                {activeTab === 'explain' && (
                    <div className={styles.infoMessage}>
                        Query plan will appear here after running <code>EXPLAIN</code>
                    </div>
                )}

                {activeTab === 'history' && (
                    <div className={styles.historyList}>
                        {history.length === 0 ? (
                            <p className={styles.infoMessage}>No queries run yet.</p>
                        ) : (
                            <ul>
                                {history.map((query, idx) => (
                                    <li key={idx} className={styles.historyItem}>
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
