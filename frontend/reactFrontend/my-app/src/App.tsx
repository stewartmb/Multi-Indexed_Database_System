import { useState } from 'react';
import ResizableSidebarLayout from './components/ResizableSidebar.tsx';
import Sidebar from './components/Sidebar.tsx';
import ResizablePanel from './components/ResizablePanel.tsx';
import { QueryUrlProvider } from './contexts/QueryUrlContext.tsx';

interface QueryResult {
    data: any[] | null;
    columns: string[] | null;
    columns_types: string[] | null; 
    table: string | null;           
    message: string | null;
    error: string | null;
    details?: string | null;
}


function App() {
    const [queryResult, setQueryResult] = useState<QueryResult>({
        data: null,
        columns: null,
        columns_types: null, 
        table: null,         
        message: null,
        error: null,
        details: null
    });

    const handleRunQuery = async (query: string) => {
    try {
        setQueryResult({
            data: null,
            columns: null,
            columns_types: null, 
            table: null,         
            message: null,
            error: null,
            details: null
        });

        const response = await fetch('http://127.0.0.1:8000/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query }),
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(JSON.stringify({
                error: result.error || 'Error executing query',
                details: result.details || ''
            }));
        }

        setQueryResult({
            data: result.data || null,
            columns: result.columns || null,
            columns_types: result.columns_types || null, 
            table: result.table || null,                 
            message: result.message || null,
            error: null,
            details: null
        });


        } catch (err: any) {
            let errorMessage = 'Error executing query';
            let errorDetails = '';

            try {
                const parsedError = JSON.parse(err.message);
                errorMessage = parsedError.error;
                errorDetails = parsedError.details;
            } catch {
                errorMessage = err.message;
            }

            setQueryResult(prev => ({
                ...prev,
                error: errorMessage,
                details: errorDetails
            }));
        }
    };


    return (
        <QueryUrlProvider>
            <ResizableSidebarLayout
                Sidebar={<Sidebar />}
                MainContent={<ResizablePanel queryResult={queryResult} onRunQuery={handleRunQuery} />}
            />
        </QueryUrlProvider>
    );
}

export default App;