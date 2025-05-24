import React, { useState } from 'react';
import TableButton from './TableButton';

interface Table {
    name: string;
    indices: string[];
}

const structure = [
    {
        name: 'Schema Lab2',
        tables: [
            { name: 'tabla', indices: ['idx_locations', 'idx_fecha'] },
            { name: 'TablaGIN', indices: ['idx_gin'] },
            { name: 'TablaGist', indices: ['idx_gist'] },
            { name: 'coseno', indices: [] },
        ] as Table[],
    },
    {
        name: 'Schema Public',
        tables: [
            { name: 'Users', indices: ['idx_users_email', 'idx_users_created_at'] },
            { name: 'Locations', indices: ['idx_destinos_ciudad_index', 'idx_orders_status'] },
            { name: 'Products', indices: ['idx_products_category'] },
            { name: 'Airports', indices: [] },
        ] as Table[],
    },
];

const Sidebar = () => {
    const [openTables, setOpenTables] = useState<Record<string, boolean>>({});

    const toggleTable = (tableName: string) => {
        setOpenTables((prev) => ({
            ...prev,
            [tableName]: !prev[tableName],
        }));
    };

    return (
        <div className="w-64 h-full bg-gray-900 text-gray-200 p-4 overflow-auto select-none">
            <h2 className="text-xl font-bold mb-6 border-b border-gray-700 pb-2">PostgreSQL</h2>
            <ul className="list-none">
                {structure.map((db, idx) => (
                    <li key={idx} className="mb-4">
                        <div className="text-lg font-semibold">{db.name}</div>
                        <ul className="mt-2 list-none">
                            {db.tables.map((table) => (
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
                            ))}
                        </ul>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default Sidebar;
