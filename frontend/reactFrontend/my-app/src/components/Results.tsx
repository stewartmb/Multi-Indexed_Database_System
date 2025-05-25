import React, { useState } from 'react';
import styles from './Results.module.css'; // Importar los estilos CSS

interface Props {
    data: any[] | null;
    message: string | null;
    error: string | null;
    history: string[];
    columns: string[];
}

const Results: React.FC<Props> = ({ data, columns, message, error, history }) => {
    const [activeTab, setActiveTab] = useState<'data' | 'messages' | 'history'>('data'); // Eliminamos 'explain'

    const headers = data && data.length > 0 ? Object.keys(data[0]) : [];

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
