import React from 'react';

interface TableButtonProps {
    tableName: string;
    isOpen: boolean;
    onToggle: () => void;
}
export default function TableButton({ tableName, isOpen, onToggle }: TableButtonProps) {
    return (
        <button
            onClick={onToggle}
            type="button"
            className="flex items-center justify-between w-full h-10 px-2 rounded hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 overflow-hidden"
            style={{
                minHeight: '50px',
                maxHeight: '130px',
                lineHeight: '1',
                marginTop: 5,
                marginRight: 120,
            }}
        >
  <span className="truncate" style={{lineHeight: '40px'}}>
    {tableName}
  </span>

            <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                stroke="currentColor"
                strokeWidth={1.5}
                viewBox="0 0 24 24"
                aria-hidden="true"
                style={{
                    width: '24px',
                    height: '24px',
                    flexShrink: 0,
                    boxSizing: 'content-box',
                    display: 'block',
                    marginTop: 'auto',
                    marginBottom: 'auto',
                }}
                className={`${isOpen ? 'rotate-90' : ''} transition-transform duration-200`}
            >
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7"/>
            </svg>
        </button>
    );
}

