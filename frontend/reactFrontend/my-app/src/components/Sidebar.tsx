import React, { useState } from 'react';
import TableButton from './TableButton';

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
    const [structureData, setStructureData] = useState<Schema[]>([]);  // Inicializamos con un arreglo vacío
    const [loading, setLoading] = useState<boolean>(false);  // Para gestionar el estado de carga
    const [error, setError] = useState<string | null>(null);  // Para gestionar posibles errores

    const toggleTable = (tableName: string) => {
        setOpenTables((prev) => ({
            ...prev,
            [tableName]: !prev[tableName],
        }));
    };

    // Función para refrescar el sidebar y obtener los datos desde el servidor
    const refreshSidebar = async () => {
        setLoading(true);  // Iniciamos el estado de carga
        setError(null);  // Limpiamos el error previo
        setStructureData([]);  // Limpiamos los datos previos

        try {
            const response = await fetch('http://127.0.0.1:8082/info');  // Hacemos la solicitud GET al backend

            if (!response.ok) {
                throw new Error('Failed to fetch data');
            }

            const data = await response.json();  // Parseamos la respuesta JSON

            // Aseguramos que `data.info` esté presente y sea un arreglo
            if (Array.isArray(data.info)) {
                setStructureData(data.info);  // Asignamos los datos si son válidos
            } else {
                setError('Datos no válidos recibidos del servidor');
            }
        } catch (err) {
            setError('Error al obtener los datos');  // Capturamos el error si ocurre
        } finally {
            setLoading(false);  // Terminamos el estado de carga
        }
    };

    return (
        <div className="w-64 h-full bg-gray-900 text-gray-200 p-4 overflow-auto select-none sidebar-container">
            <h2 className="text-xl font-bold mb-6 border-b border-gray-700 pb-2">PostgreSQL</h2>

            {/* Botón de refresh */}
            <button
                className="bg-blue-500 hover:bg-blue-700 text-white py-2 px-4 rounded mb-4 w-full"
                onClick={refreshSidebar}
                disabled={loading}  // Deshabilitamos el botón mientras cargamos
            >
                {loading ? 'Cargando...' : 'Refresh'}
            </button>

            {error && <div className="text-red-500 mb-4">{error}</div>}  {/* Mostramos el error si ocurre */}

            {/* Verificamos si structureData está vacío */}
            {structureData.length === 0 ? (
                <div className="text-gray-500">No hay esquemas o tablas disponibles.</div>
            ) : (
                <ul className="list-none">
                    {structureData.map((db, idx) => (
                        <li key={idx} className="mb-4">
                            <div className="text-lg font-semibold">{db.name}</div>
                            <ul className="mt-2 list-none">
                                {db.tables.length === 0 ? (
                                    <li className="text-sm text-gray-500">No hay tablas en este esquema</li>
                                ) : (
                                    db.tables.map((table) => (
                                        <li key={table.name} className="mb-1">
                                            <TableButton
                                                tableName={table.name}
                                                isOpen={!!openTables[table.name]}
                                                onToggle={() => toggleTable(table.name)}
                                            />
                                            {openTables[table.name] && (
                                                <ul className="mt-1 ml-4 border-l border-gray-700 pl-3 text-sm text-gray-400 list-none">
                                                    {table.indices.length > 0 ? (
                                                        table.indices.map((idx) => (
                                                            <li
                                                                key={idx}
                                                                className="py-0.5 hover:text-gray-200 cursor-pointer"
                                                                title={`Índice: ${idx}`}
                                                            >
                                                                {idx}
                                                            </li>
                                                        ))
                                                    ) : (
                                                        <li className="py-0.5 italic text-gray-500">No indices</li>
                                                    )}
                                                </ul>
                                            )}
                                        </li>
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
