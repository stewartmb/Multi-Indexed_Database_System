import React, { useState } from 'react';
import SQLEditor from './SQLEditor';
import Results from './Results';
import ResizableLayout from './ResizableLayout';

export default function ResizablePanel() {
    const [data, setData] = useState<any[] | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [history, setHistory] = useState<string[]>([]);

    const runQuery = async (query: string) => {
        setData(null);
        setError(null);

        // Agrega al historial antes de ejecutar
        setHistory((prev) => [query, ...prev]);

        // TODO: CAMBIAR EL PUERTO A 8000
        try {
            console.log('Running query:', query);
            const response = await fetch('http://127.0.0.1:8080/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query }),
            });

            console.log('Response:', response);

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.details || 'Query failed');
            }

            if (Array.isArray(result)) {
                setData(result);
            } else if (result.data) {
                setData(result.data);
            } else {
                setData([]);
            }
        } catch (err: any) {
            console.error('Error running query:', err);
            setError(err.message);
        }
    };

    return (
        <ResizableLayout
            top={<SQLEditor onRun={runQuery} />}
            bottom={<Results data={data} error={error} history={history} />}
        />
    );
}
