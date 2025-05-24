import React, { useRef, useState, useEffect } from 'react';

interface ResizableSidebarLayoutProps {
    Sidebar: React.ReactNode;
    MainContent: React.ReactNode;
}

export default function ResizableSidebarLayout({ Sidebar, MainContent }: ResizableSidebarLayoutProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const isDragging = useRef(false);
    const [sidebarWidth, setSidebarWidth] = useState(300); // ancho inicial en px

    const onMouseDown = (e: React.MouseEvent) => {
        e.preventDefault();
        isDragging.current = true;
    };

    const onMouseUp = () => {
        isDragging.current = false;
    };

    const onMouseMove = (e: MouseEvent) => {
        if (!isDragging.current) return;
        if (!containerRef.current) return;

        const rect = containerRef.current.getBoundingClientRect();
        let newWidth = e.clientX - rect.left;

        if (newWidth < 100) newWidth = 100;
        if (newWidth > rect.width - 100) newWidth = rect.width - 100;

        setSidebarWidth(newWidth);
    };

    useEffect(() => {
        window.addEventListener('mouseup', onMouseUp);
        window.addEventListener('mousemove', onMouseMove);
        return () => {
            window.removeEventListener('mouseup', onMouseUp);
            window.removeEventListener('mousemove', onMouseMove);
        };
    }, []);

    return (
        <div ref={containerRef} className="flex h-screen w-screen select-none">
            <div style={{ width: sidebarWidth }} className="h-full bg-gray-800 text-white overflow-auto">
                {Sidebar}
            </div>

            {/* Barra divisora más ancha y con cursor visible */}
            <div
                onMouseDown={onMouseDown}
                className="w-4 cursor-col-resize bg-gray-600 hover:bg-gray-800"
                title="Arrastra para redimensionar"
                style={{ userSelect: 'none' }}
            >
                {/* Para que se vea mejor, un pequeño indicador central */}
                <div
                    style={{
                        width: '2px',
                        height: '40px',
                        backgroundColor: '#fff',
                        margin: 'auto',
                        borderRadius: '1px',
                        marginTop: 'calc(50% - 20px)',
                    }}
                />
            </div>

            <div style={{ flex: 1 }} className="h-full bg-gray-100 overflow-auto">
                {MainContent}
            </div>
        </div>
    );
}
