// components/ResizableLayout.tsx
import React, { useRef, useEffect, useState } from 'react';

interface Props {
    top: React.ReactNode;
    bottom: React.ReactNode;
}

const ResizableLayout: React.FC<Props> = ({ top, bottom }) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const [topHeight, setTopHeight] = useState(200);
    const isDragging = useRef(false);

    const onMouseDown = (e: React.MouseEvent) => {
        e.preventDefault();
        isDragging.current = true;
    };

    const onMouseUp = () => {
        isDragging.current = false;
    };

    const onMouseMove = (e: MouseEvent) => {
        if (!isDragging.current || !containerRef.current) return;

        const rect = containerRef.current.getBoundingClientRect();
        let newHeight = e.clientY - rect.top;

        newHeight = Math.max(50, Math.min(newHeight, rect.height - 50));
        setTopHeight(newHeight);
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
        <div
            ref={containerRef}
            className={`flex flex-col w-full h-full ${isDragging.current ? 'select-none' : 'select-auto'}`}
            style={{ 
                background: 'linear-gradient(145deg, #0f172a, #1e293b)',
                border: '2px solid #374151',
                borderRadius: '0.75rem',
                overflow: 'hidden',
                boxShadow: '0 10px 30px rgba(0, 0, 0, 0.3)'
            }}
        >
            <div 
                style={{ 
                    height: topHeight, 
                    background: 'linear-gradient(145deg, #0f172a, #1e293b)',
                    borderRadius: '0.75rem 0.75rem 0 0',
                    overflow: 'hidden'
                }}
            >
                {top}
            </div>

            <div
                onMouseDown={onMouseDown}
                style={{
                    height: '12px',
                    background: 'linear-gradient(145deg, #374151, #4b5563)',
                    cursor: 'row-resize',
                    alignSelf: 'stretch',
                    position: 'relative',
                    transition: 'all 0.2s ease',
                    borderTop: '1px solid #6b7280',
                    borderBottom: '1px solid #6b7280',
                }}
                title="Drag to resize"
                onMouseEnter={(e) => {
                    e.currentTarget.style.background = 'linear-gradient(145deg, #4b5563, #6b7280)';
                }}
                onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'linear-gradient(145deg, #374151, #4b5563)';
                }}
            >
                {/* Visual indicator for drag handle */}
                <div style={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    width: '40px',
                    height: '3px',
                    background: 'linear-gradient(90deg, #9ca3af, #d1d5db, #9ca3af)',
                    borderRadius: '2px',
                    opacity: 0.7
                }} />
            </div>

            <div
                style={{
                    flex: 1,
                    background: 'linear-gradient(145deg, #0f172a, #1e293b)',
                    overflow: 'auto',
                    borderRadius: '0 0 0.75rem 0.75rem'
                }}
            >
                {bottom}
            </div>
        </div>
    );
};

export default ResizableLayout;