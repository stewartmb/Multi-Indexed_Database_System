import React, { useState, useEffect } from 'react';
import '../styles/Sidebar.css';
import logoElefante from '../assets/elefante1.png';
import emptyData from '../assets/emptydata.png';
import logoTabla from '../assets/tabla.png';
import { useQueryUrl } from '../contexts/QueryUrlContext';



// Definimos las interfaces
interface Table {
    name: string;
    indices: string[];
}

interface Schema {
    name: string;
    tables: Table[];
}

const Sidebar = () => {
    const [openTables, setOpenTables] = useState<Record<string, boolean>>({});
    const [hoverTable, setHoverTable] = useState<string | null>(null);
    const [structureData, setStructureData] = useState<Schema[]>([]);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [openSchemas, setOpenSchemas] = useState<string[]>([]);
    const [tempUrl, setTempUrl] = useState('http://127.0.0.1:8000');
    const { queryUrl, setQueryUrl } = useQueryUrl();

    useEffect(() => {
        if (!queryUrl) {
            setQueryUrl('http://127.0.0.1:8087');
        }
    }, []);

    const handleUrlSubmit = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (tempUrl.trim()) {
            setQueryUrl(tempUrl.trim());
            refreshSidebar();
        }
    };

    const toggleTable = (tableName: string) => {
        setOpenTables((prev) => ({
            ...prev,
            [tableName]: !prev[tableName],
        }));
    };

    const toggleSchema = (name: string) => {
        setOpenSchemas((prev) =>
            prev.includes(name)
                ? prev.filter((n) => n !== name)
                : [...prev, name]
        );
    };

    const refreshSidebar = async () => {
        setLoading(true);
        setError(null);
        setStructureData([]);

        if (!queryUrl) {
            setError('No URL configured. Please set a URL first.');
            setLoading(false);
            return;
        }

        try {
            console.log("debug4", queryUrl)
            const response = await fetch(`${queryUrl}/info`);

            if (!response.ok) {
                throw new Error(`Failed to fetch data: ${response.statusText}`);
            }

            const data = await response.json();

            if (Array.isArray(data.info)) {
                setStructureData(data.info);
            } else {
                setError('Invalid data received from server');
            }
        } catch (err) {
            setError(`Error: ${err instanceof Error ? err.message : 'Failed to connect to server'}`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="sidebar-container">
            <h2 className="sidebar-title">
                <img src={logoElefante} className="sidebar-logo"/>
                <a href="#" className="db-link">
                    <span className="postgre">Postgre</span><span className="sql">SQL</span>
                </a>
            </h2>

            {/* URL Form */}
            <form onSubmit={handleUrlSubmit} className="url-form">
                <input
                    type="text"
                    className="url-input"
                    placeholder="http://127.0.0.1:8000"
                    value={tempUrl}
                    onChange={(e) => setTempUrl(e.target.value)}
                />
                <div className="button-group">
                    <button
                        type="submit"
                        className="btn-set-url"
                    >
                        <svg className="inline-block w-4 h-4 mr-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M21 12h-8M3 12h8M12 3v18" />
                        </svg>
                        Set URL
                    </button>
                    <button
                        type="button"
                        className={`btn-refresh ${loading ? 'loading' : ''}`}
                        onClick={refreshSidebar}
                        disabled={loading}
                    >
                        <svg className="inline-block w-4 h-4 mr-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M21.5 2v6h-6M2.5 22v-6h6M2 12c0-4.4 3.6-8 8-8 3.4 0 6.3 2.1 7.4 5M22 12c0 4.4-3.6 8-8 8-3.4 0-6.3-2.1-7.4-5" />
                        </svg>
                        {loading ? 'Loading...' : 'Refresh'}
                    </button>
                </div>
            </form>

            {/* Mensaje de error */}
            {error && (
                <div className="error-message">
                    {error}
                </div>
            )}

            {/* Contenido principal */}
            {loading && structureData.length === 0 ? (
                <div className="loading-state">
                    <div className="loading-spinner"></div>
                    Cargando esquemas...
                </div>
            ) : structureData.length === 0 ? (
                <div className="empty-state">
                    <img src={emptyData} className="empty-logo"/>

                    <br/>No hay esquemas o tablas disponibles.
                </div>
            ) : (
                <ul className="schema-list">
                    {structureData.map((db, idx) => (
                        <li key={idx} className="schema-item">
                            <div
                                className="schema-name"
                                onClick={() => toggleSchema(db.name)}
                                style={{ cursor: 'pointer' }}
                            >
                                {db.name}
                            </div>

                            {openSchemas.includes(db.name) && (
                                <ul className="table-list">
                                    {db.tables.length === 0 ? (
                                        <li className="no-tables-message">No hay tablas en este esquema</li>
                                    ) : (
                                        db.tables.map((table) => (
                                            <div key={table.name} className="table">
                                                <div
                                                    className="table-header"
                                                    onMouseEnter={() => setHoverTable(table.name)}
                                                    onMouseLeave={() => setHoverTable(null)}
                                                    onClick={() => toggleTable(table.name)}
                                                >
                                                    <img src={logoTabla} className="sidebar-logo"
                                                    style={{width: "20px",
                                                        opacity: "40%",
                                                        marginRight: "5px",
                                                        marginTop: "4px"
                                                    }}/>
                                                    <span style={{color : "#dddddd"}}>
                                                            {table.name}</span>
                                                    <span> &nbsp;&nbsp;({table.indices.length} atributos)</span>
                                                </div>

                                                <div className="table-indices">
                                                    {table.indices.length > 0 ? (
                                                        table.indices.map((idx, index) => {
                                                            const [firstWord, ...rest] = idx.split(' ');
                                                            return (
                                                                <div key={index} className="flex justify-between py-1">
                                                                    <span style={{ fontSize: '0.9rem' }}>{firstWord}</span>
                                                                    <span
                                                                        className="text-right text-gray-600"
                                                                        style={{
                                                                            fontSize: '0.7rem',
                                                                            fontFamily: 'monospace',
                                                                        }}
                                                                    >
                      {rest.join(' ')}
                    </span>
                                                                </div>
                                                            );
                                                        })
                                                    ) : (
                                                        <div>No indices</div>
                                                    )}
                                                </div>
                                            </div>
                                        ))
                                    )}
                                </ul>
                            )}

                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default Sidebar;