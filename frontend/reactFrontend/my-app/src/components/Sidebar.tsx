import React, { useState } from 'react';
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
    const [openSchemas, setOpenSchemas] = useState([]);


    const { queryUrl } = useQueryUrl();

    const toggleTable = (tableName: string) => {
        setOpenTables((prev) => ({
            ...prev,
            [tableName]: !prev[tableName],
        }));
    };

    const toggleSchema = (name) => {
        setOpenSchemas((prev) =>
            prev.includes(name)
                ? prev.filter((n) => n !== name)
                : [...prev, name]
        );
    };

    // Función para refrescar el sidebar y obtener los datos desde el servidor
    const refreshSidebar = async () => {
        setLoading(true);
        setError(null);
        setStructureData([]);

        try { // TODO: CAMBIAR A 8000 el puerto
            const response = await fetch(`${queryUrl}/info`);

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