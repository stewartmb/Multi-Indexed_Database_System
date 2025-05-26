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

        if (newWidth < 55) newWidth = 55;
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
        <div ref={containerRef} className="flex h-screen w-screen select-none ">
        {/* Sidebar */}
            <div style={{width: sidebarWidth}} className="h-full w-full bg-gray-200 overflow-auto">
                {Sidebar}
            </div>

            {/* Barra divisora */}
            <div
                onMouseDown={onMouseDown}
                className="cursor-col-resize"
                title="Drag to resize"
                style={{ 
                    userSelect: 'none', 
                    width: '10px',
                    background: 'linear-gradient(145deg, #0f172a,rgb(14, 18, 26))',
                    position: 'relative',
                    transition: 'all 0.2s ease',
                    borderLeft: '1px solid #374151',
                    borderRight: '1px solid #374151',
                }}
                onMouseEnter={(e) => {
                    e.currentTarget.style.background = 'linear-gradient(145deg,rgb(8, 21, 41),rgb(8, 36, 85))';
                }}
                onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'linear-gradient(145deg,rgb(4, 12, 31),rgb(0, 0, 0))';
                }}
            >
                {/* Visual indicator for drag handle */}
                <div style={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    height: '40px',
                    width: '3px',
                    background: 'linear-gradient(180deg, #374151, #4b5563, #374151)',
                    borderRadius: '2px',
                    opacity: 0.5
                }} />
            </div>

        {/* Main content */}
        <div style={{ flex: 1 }} className="h-full bg-gray-100 overflow-hidden">
            {MainContent}
        </div>
    </div>
);
}
