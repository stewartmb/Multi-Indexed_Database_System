import { useState } from 'react';
import ResizableSidebarLayout from './components/ResizableSidebar.tsx';
import Sidebar from './components/Sidebar.tsx';
import ResizablePanel from './components/ResizablePanel.tsx';
import { QueryUrlProvider, useQueryUrl } from './contexts/QueryUrlContext.tsx';

function AppContent() {
    const [results, setResults] = useState<any[] | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [message, setMessage] = useState<string | null>(null);
    const [columns, setColumns] = useState<string[]>([]);
    const { queryUrl } = useQueryUrl();

    const handleRunQuery = async (query: string) => {
        try {
            setError(null);
            setResults(null);
            setMessage(null);
            setColumns([]);

            if (!queryUrl) {
                throw new Error('No URL configured. Please set a URL first.');
            }

            console.log('Sending query:', query);
            const response = await fetch(`${queryUrl}/query`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({ query }),
            });

            if (!response.ok) {
                const errorText = await response.text();
                const errorData = errorText ? JSON.parse(errorText) : null;
                throw new Error(errorData?.message || errorData?.error || errorText || 'Error executing query');
            }

            const data = await response.json();
            console.log('Raw query response:', data);
            console.log('Response type:', typeof data);
            console.log('Response structure:', {
                hasData: 'data' in data,
                hasColumns: 'columns' in data,
                dataType: data.data ? typeof data.data : 'undefined',
                isDataArray: data.data ? Array.isArray(data.data) : false
            });
            
            let processedResults = null;
            let processedColumns = [];

            // Handle the specific response format
            if (data.columns && Array.isArray(data.data)) {
                processedResults = data.data.map((row: any[]) => {
                    // Create an object mapping columns to values
                    const rowObj: { [key: string]: any } = {};
                    data.columns.forEach((col: string, index: number) => {
                        rowObj[col] = row[index];
                    });
                    return rowObj;
                });
                processedColumns = data.columns;
                console.log('Processing array data with columns');
            } else if (data.data && Array.isArray(data.data)) {
                // Fallback for other data formats
                processedResults = data.data;
                processedColumns = data.columns || Object.keys(data.data[0] || {});
                console.log('Processing as data format');
            }

            console.log('Processed data:', {
                results: processedResults,
                columns: processedColumns,
                sampleRow: processedResults && processedResults[0] ? processedResults[0] : null
            });

            setResults(processedResults);
            setColumns(processedColumns);
            setMessage(data.message || 'Query executed successfully');

        } catch (err: any) {
            console.error('Query error:', err);
            setError(err.message);
        }
    };

    return (
        <ResizableSidebarLayout
            Sidebar={<Sidebar />}
            MainContent={<ResizablePanel 
                onRunQuery={handleRunQuery} 
                results={results} 
                error={error}
                message={message}
                columns={columns}
            />}
        />
    );
}

function App() {
    return (
        <QueryUrlProvider>
            <AppContent />
        </QueryUrlProvider>
    );
}

export default App;