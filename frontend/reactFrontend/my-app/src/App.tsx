import { useState } from 'react';
import ResizableSidebarLayout from './components/ResizableSidebar.tsx';
import Sidebar from './components/Sidebar.tsx';
import ResizablePanel from './components/ResizablePanel.tsx';
import { QueryUrlProvider } from './contexts/QueryUrlContext.tsx';


function App() {
    const [results, setResults] = useState<any[] | null>(null);
    const [error, setError] = useState<string | null>(null);

    const handleRunQuery = async (query: string) => {
        try {
            setError(null);
            setResults(null);

            // Simulando una llamada a la API
            const response = await fetch('/api/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query }),
            });

            if (!response.ok) throw new Error('Error ejecutando la consulta');

            const data = await response.json();
            setResults(data.rows || []);
        } catch (err: any) {
            setError(err.message);
        }
    };

    return (
        <QueryUrlProvider>
            <ResizableSidebarLayout
                Sidebar={<Sidebar />}
                MainContent={<ResizablePanel />}
            />
        </QueryUrlProvider>
    );
}

export default App;