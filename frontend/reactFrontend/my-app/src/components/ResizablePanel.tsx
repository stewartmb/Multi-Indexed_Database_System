import React, { useState } from 'react';
import SQLEditor from './SQLEditor';
import Results from './results/Results.tsx';
import ResizableLayout from './ResizableLayout';
import { useQueryUrl } from '../contexts/QueryUrlContext';

interface ResizablePanelProps {
    onRunQuery?: (query: string) => Promise<void>;
    results?: any[] | null;
    error?: string | null;
    message?: string | null;
    columns?: string[];
}

export default function ResizablePanel({ 
    onRunQuery, 
    results: externalResults, 
    error: externalError,
    message: externalMessage,
    columns: externalColumns 
}: ResizablePanelProps) {
    const [data, setData] = useState<any[] | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [history, setHistory] = useState<string[]>([]);
    const [message, setMessage] = useState<string | null>(null);
    const [columns, setColumns] = useState<string[]>([]);
    const [currentQuery, setCurrentQuery] = useState<string>('');
    const [isLoading, setIsLoading] = useState<boolean>(false);

    const { queryUrl } = useQueryUrl();

    const runQuery = async (query: string) => {
        if (onRunQuery) {
            // Use external query handler if provided
            await onRunQuery(query);
            setHistory((prev) => [query, ...prev]); // Still update history when using external handler
            return;
        }

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

        // Add to history before executing
        setHistory((prev) => [query, ...prev]);

        try {
            console.log('Running query:', query);
            if (!queryUrl) {
                throw new Error('No URL configured. Please set a URL first.');
            }

            const response = await fetch(`${queryUrl}/query`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({ query }),
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.message || result.error || result.details || 'Query failed');
            }

            console.log('Response:', result);

            if (Array.isArray(result.data)) {
                setData(result.data);
                // First try to get columns from the response, then from data keys
                const responseColumns = result.columns || (result.data[0] ? Object.keys(result.data[0]) : []);
                setColumns(responseColumns);
                setMessage(result.message || 'Query executed successfully');
            } else if (Array.isArray(result.rows)) {
                setData(result.rows);
                // First try to get columns from the response, then from rows keys
                const responseColumns = result.columns || (result.rows[0] ? Object.keys(result.rows[0]) : []);
                setColumns(responseColumns);
                setMessage(result.message || 'Query executed successfully');
            } else {
                setData([]);
                setColumns([]);
                setMessage(result.message || 'Query executed with no results');
            }
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

    // Use external values if provided
    const displayData = externalResults ?? data;
    const displayError = externalError ?? error;
    const displayMessage = externalMessage ?? message;
    const displayColumns = externalColumns ?? columns;

    return (
        <ResizableLayout
            top={<SQLEditor onRun={runQuery} query={currentQuery} onQueryChange={setCurrentQuery} isLoading={isLoading} />}
            bottom={<Results 
                data={displayData} 
                columns={displayColumns} 
                message={displayMessage} 
                error={displayError} 
                history={history} 
                onSelectHistory={handleQueryFromHistory} 
                isLoading={isLoading} 
            />}
        />
    );
}