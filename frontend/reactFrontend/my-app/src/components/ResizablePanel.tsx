import React, { useState } from 'react';
import SQLEditor from './SQLEditor';
import Results from './results/Results.tsx';
import ResizableLayout from './ResizableLayout';
import { useQueryUrl } from '../contexts/QueryUrlContext';


export default function ResizablePanel() {
    const [data, setData] = useState<any[] | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [history, setHistory] = useState<string[]>([]);
    const [message, setMessage] = useState<string | null>(null);
    const [columns, setColumns] = useState<string[]>([]);
    const [currentQuery, setCurrentQuery] = useState<string>('');
    const [isLoading, setIsLoading] = useState<boolean>(false);

    const { queryUrl } = useQueryUrl();

    const runQuery = async (query: string) => {
        // Prevent execution if already loading
        if (isLoading) {
            console.log('Query already in progress, ignoring new request');
            return;
        }

        setIsLoading(true);
        setData(null);
        setError(null);
        setColumns([]);
        setMessage(null);

        // Agrega al historial antes de ejecutar
        setHistory((prev) => [query, ...prev]);

        // TODO: CAMBIAR EL PUERTO A 8000
        try {
            console.log('Running query:', query);
            const response = await fetch(`${queryUrl}/query`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query }),
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.details || 'Query failed');
            }

            console.log('Response:', result);

            setData(result.data);
            setColumns(result.columns);
            setMessage(result.message || null);
        } catch (err: any) {
            console.error('Error running query:', err);
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    const handleQueryFromHistory = (query: string) => {
        setCurrentQuery(query);
    };

    return (
        <ResizableLayout
            top={<SQLEditor onRun={runQuery} query={currentQuery} onQueryChange={setCurrentQuery} isLoading={isLoading} />}
            bottom={<Results data={data} columns={columns} message={message} error={error} history={history} onSelectHistory={handleQueryFromHistory} isLoading={isLoading} />}
        />
    );
}