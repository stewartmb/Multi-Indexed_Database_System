import React, { useState } from 'react';
import './Sidebar.css';
import logoElefante from '../assets/elefante1.png';

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

    const toggleTable = (tableName: string) => {
        setOpenTables((prev) => ({
            ...prev,
            [tableName]: !prev[tableName],
        }));
    };

    // Función para refrescar el sidebar y obtener los datos desde el servidor
    const refreshSidebar = async () => {
        setLoading(true);
        setError(null);
        setStructureData([]);

        try { // TODO: CAMBIAR A 8000 el puerto
            const response = await fetch('http://127.0.0.1:8084/info');

            if (!response.ok) {
                throw new Error('Failed to fetch data');
            }

            const data = await response.json();

            // Aseguramos que `data.info` esté presente y sea un arreglo
            if (Array.isArray(data.info)) {
                setStructureData(data.info);
            } else {
                setError('Datos no válidos recibidos del servidor');
            }
        } catch (err) {
            setError('Error al obtener los datos');
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

            {/* Botón de refresh */}
            <button
                className={`refresh-button ${loading ? 'loading' : ''}`}
                onClick={refreshSidebar}
                disabled={loading}
            >
                {loading ? 'Cargando...' : 'Refresh'}
            </button>

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
                    No hay esquemas o tablas disponibles.
                </div>
            ) : (
                <ul className="schema-list">
                    {structureData.map((db, idx) => (
                        <li key={idx} className="schema-item">
                            <div className="schema-name">
                                {db.name}
                            </div>
                            <ul className="table-list">
                                {db.tables.length === 0 ? (
                                    <li className="no-tables-message">
                                        No hay tablas en este esquema
                                    </li>
                                ) : (
                                    db.tables.map((table) => (
                                        <div className="table">
                                            <div className="table-header"
                                                 onMouseEnter={() => setHoverTable(table.name)}
                                                 onMouseLeave={() => setHoverTable(null)}
                                                 onClick={() => toggleTable(table.name)}
                                            >
                                                {table.name}
                                                <span> ({table.indices.length} atributos)</span>
                                            </div>

                                            <div className="table-indices">
                                                {table.indices.length > 0 ? (
                                                    table.indices.map((idx, index) => {
                                                        const [firstWord, ...rest] = idx.split(' ');
                                                        return (
                                                            <div key={index}
                                                                 className="flex justify-between py-1">
                                                                <span className="text-white-600" style={
                                                                    {fontSize: '0.9rem'}
                                                                }>{firstWord}</span>
                                                                <span
                                                                    className="text-right text-gray-600" style={
                                                                    {fontSize: '0.7rem', fontFamily: 'monospace'}
                                                                }>{rest.join(' ')}</span>
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
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default Sidebar;