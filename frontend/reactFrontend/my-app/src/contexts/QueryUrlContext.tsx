import React, { createContext, useContext, useState, ReactNode } from 'react';

// Tipo del contexto
interface QueryUrlContextType {
    queryUrl: string;
    setQueryUrl: (url: string) => void;
}

// Valor inicial vacío (se sobreescribe por el Provider)
const QueryUrlContext = createContext<QueryUrlContextType | null>(null);

// Provider con tipado de props
export const QueryUrlProvider = ({ children }: { children: ReactNode }) => {
    const [queryUrl, setQueryUrl] = useState('http://127.0.0.1:8085/query');

    return (
        <QueryUrlContext.Provider value={{ queryUrl, setQueryUrl }}>
            {children}
        </QueryUrlContext.Provider>
    );
};

// Hook personalizado
export const useQueryUrl = (): QueryUrlContextType => {
    const context = useContext(QueryUrlContext);
    if (!context) {
        throw new Error('useQueryUrl debe usarse dentro de <QueryUrlProvider>');
    }
    return context;
};
