import React, { useState, useRef, useEffect } from 'react';
import SQLEditor from './SQLEditor';
import Results from './Results';

export default function ResizablePanel() {
    const containerRef = useRef<HTMLDivElement>(null);
    const [topHeight, setTopHeight] = useState(200); // px
    const isDragging = useRef(false);

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
        let newHeight = e.clientY - rect.top;

        if (newHeight < 50) newHeight = 50;
        if (newHeight > rect.height - 50) newHeight = rect.height - 50;

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
                border: '2px solid black',
            }}
        >
            <div
                style={{
                    height: topHeight,
                    backgroundColor: '#a0c4ff',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                }}
            >
                <SQLEditor onRun={(query) => console.log('Running query:', query)} />
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
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                }}
            >
                <Results data={null} error={null} />
            </div>
        </div>
    );
}
