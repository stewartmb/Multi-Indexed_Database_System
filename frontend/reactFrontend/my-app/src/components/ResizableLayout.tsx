// components/ResizableLayout.tsx
import React, { useState, useRef, useEffect } from 'react';
import styles from '../styles/ResizableLayout.module.css';

interface Props {
    topContent: React.ReactNode;
    bottomContent: React.ReactNode;
}

const ResizableLayout: React.FC<Props> = ({ topContent, bottomContent }) => {
    const [topHeight, setTopHeight] = useState('50%');
    const containerRef = useRef<HTMLDivElement>(null);
    const isDraggingRef = useRef(false);
    const startYRef = useRef(0);
    const startHeightRef = useRef(0);

    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            if (!isDraggingRef.current || !containerRef.current) return;

            const containerHeight = containerRef.current.offsetHeight;
            const deltaY = e.clientY - startYRef.current;
            const newHeight = Math.min(Math.max(startHeightRef.current + deltaY, 100), containerHeight - 100);
            
            setTopHeight(`${(newHeight / containerHeight) * 100}%`);
        };

        const handleMouseUp = () => {
            isDraggingRef.current = false;
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
        };

        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);

        return () => {
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);
        };
    }, []);

    const handleMouseDown = (e: React.MouseEvent) => {
        if (!containerRef.current) return;

        isDraggingRef.current = true;
        startYRef.current = e.clientY;
        startHeightRef.current = containerRef.current.offsetHeight * (parseInt(topHeight as string) / 100);
        
        document.body.style.cursor = 'row-resize';
        document.body.style.userSelect = 'none';
    };

    return (
        <div ref={containerRef} className={styles.container}>
            <div style={{ height: topHeight }} className={styles.topPanel}>
                {topContent}
            </div>
            <div
                className={styles.dragBar}
                onMouseDown={handleMouseDown}
            >
                <div className={styles.dragBarInner}></div>
            </div>
            <div style={{ height: `calc(100% - ${topHeight} - 8px)` }} className={styles.bottomPanel}>
                {bottomContent}
            </div>
        </div>
    );
};

export default ResizableLayout;