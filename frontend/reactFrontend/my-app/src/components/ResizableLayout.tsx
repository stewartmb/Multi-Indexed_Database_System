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
            style={{ border: '2px solid black' }}
        >
            <div style={{ height: topHeight, backgroundColor: '#a0c4ff' }}>
                {top}
            </div>

            <div
                onMouseDown={onMouseDown}
                style={{
                    height: '10px',
                    backgroundColor: '#0077b6',
                    cursor: 'row-resize',
                    alignSelf: 'stretch',
                }}
                title="Arrastra para redimensionar"
            />

            <div
                style={{
                    flex: 1,
                    backgroundColor: '#caf0f8',
                    overflow: 'auto',
                }}
            >
                {bottom}
            </div>
        </div>
    );
};

export default ResizableLayout;
