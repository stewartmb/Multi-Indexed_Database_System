import React, { useState, useEffect } from 'react';
import CodeMirror from '@uiw/react-codemirror';
import { sql } from '@codemirror/lang-sql';
import { EditorView, ViewPlugin, Decoration } from "@codemirror/view";
import { HighlightStyle, syntaxHighlighting } from '@codemirror/language';
import { tags as t } from '@lezer/highlight';
import { useQueryUrl } from '../contexts/QueryUrlContext.tsx';
import {completeFromList} from "@codemirror/autocomplete";
import fileIcon from '../assets/file_icon.png';

import '../styles/SQLEditor.css';

import type { ViewUpdate, DecorationSet } from "@codemirror/view";
import { RangeSetBuilder } from "@codemirror/state";

// 🎨 Palabras específicas y sus colores
const specialWords: Record<string, string> = {
  BPTREE: "#38bdf8",
  SEQ: "#38bdf8",
  ISAM: "#38bdf8",
  HASH: "#38bdf8",
  BRIN: "#38bdf8",
  RTREE: "#38bdf8",
  BOOL: "#38bdf8",
  LONG: "#38bdf8",
  ULONG: "#38bdf8",
  CLOSEST: "#9d9af5",
  COPY: "#9d9af5",
};

const specialWordRegex = new RegExp(`\\b(${Object.keys(specialWords).join("|")})\\b`, "gi");

// 🔍 Plugin que aplica decoraciones personalizadas
const customHighlightPlugin = ViewPlugin.fromClass(
  class {
    decorations: DecorationSet;

    constructor(view: EditorView) {
      this.decorations = this.buildDecorations(view);
    }

    update(update: ViewUpdate) {
      if (update.docChanged || update.viewportChanged) {
        this.decorations = this.buildDecorations(update.view);
      }
    }
    
    buildDecorations(view: EditorView): DecorationSet {
      const builder = new RangeSetBuilder<Decoration>();
      const docText = view.state.doc.toString();
      let match;
      specialWordRegex.lastIndex = 0;
      while ((match = specialWordRegex.exec(docText)) !== null) {
        const start = match.index;
        const end = start + match[0].length;
        const word = match[0].toUpperCase();
        const color = specialWords[word];
        if (!color) continue;

        const deco = Decoration.mark({
          class: "special-word",
          attributes: { 
            style: `color: ${color} !important; font-weight: bold !important;`,
            "data-word": word
          }
        });
        builder.add(start, end, deco);
      }
      return builder.finish();
    }
  },
  { decorations: v => v.decorations }
);

interface Props {
  onRun: (query: string) => void;
  query?: string;
  onQueryChange?: (query: string) => void;
  isLoading?: boolean;
}

const myHighlightStyle = HighlightStyle.define([
  { tag: t.keyword, color: "#9d9af5" },
  { tag: t.typeName, color: "#38bdf8" },
  { tag: t.string, color: "#4ade80" },
  { tag: t.number, color: "#00eeee" },
  { tag: t.operator, color: "#dbd1c5" },
  { tag: t.variableName, color: "#e879f9" },
  { tag: t.comment, color: "#64748b", fontStyle: "italic" },
  { tag: t.punctuation, color: "#cbd5e1" },
]);

const myTheme = EditorView.theme({
  "&": {
    backgroundColor: "#1e1e1e",
    color: "#e2e8f0",
    height: "100%"
  },
  ".cm-content": {
    fontFamily: "'JetBrains Mono', monospace",
    padding: "0.5rem 0"
  },
  ".cm-line": {
    padding: "0 1rem"
  },
  ".cm-gutters": {
    backgroundColor: "#1e1e1e",
    border: "none",
    borderRight: "1px solid #2d3748",
    color: "#4a5568"
  },
  ".cm-activeLineGutter, .cm-activeLine": {
    backgroundColor: "rgba(30, 41, 59, 0.5)"
  },
  ".cm-selectionBackground": {
    backgroundColor: "rgba(70, 70, 70, 0.55) !important"
  },
  ".cm-cursor": {
    borderLeft: "2px solid #94a3b8"
  },
  "&.cm-focused .cm-selectionBackground": {
    backgroundColor: "rgba(15, 99, 138, 0.62) !important"
  },
  "&.cm-focused .cm-cursor": {
    borderLeftColor: "#e2e8f0"
  },
  ".special-word": {
    position: "relative",
    zIndex: "999",
    color: "inherit !important"
  },
});

const SQLEditor: React.FC<Props> = ({ onRun, query = '', onQueryChange, isLoading = false }) => {
  const [localQuery, setLocalQuery] = useState(query);
  const [showEditor, setShowEditor] = useState(true);
  const [files, setFiles] = useState<{ url: string; isImage: boolean; name: string; file: File }[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [copiedMessage, setCopiedMessage] = useState<string | null>(null);
  const { queryUrl } = useQueryUrl();

    const handleCopyName = async (name: string) => {
    try {
        await navigator.clipboard.writeText(name);
        setCopiedMessage(`Copied: ${name}`);
        setTimeout(() => setCopiedMessage(null), 3000); // Ocultar después de 2 segundos
    } catch (err) {
        console.error('Failed to copy!', err);
    }
    };

  useEffect(() => {
    setLocalQuery(query);
  }, [query]);

  const handleQueryChange = (value: string) => {
    setLocalQuery(value);
    if (onQueryChange) {
      onQueryChange(value);
    }
  };

  const handleClear = () => {
    setLocalQuery('');
    if (onQueryChange) {
      onQueryChange('');
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newFiles = e.target.files;
    if (!newFiles) return;

    const fileObjs: { url: string; isImage: boolean; name: string; file: File }[] = [];
    Array.from(newFiles).forEach(file => {
      const url = URL.createObjectURL(file);
      const isImage = file.type.startsWith("image/");
      fileObjs.push({ url, isImage, name: file.name , file });
    });

    setFiles(prev => [...prev, ...fileObjs]);
  };

  const handleRemoveFile = (index: number) => {
    setFiles(prev => {
      URL.revokeObjectURL(prev[index].url);
      return prev.filter((_, i) => i !== index);
    });
  };

  const toggleEditor = () => {
    setShowEditor(prev => !prev);
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const newFiles = e.dataTransfer.files;
    if (!newFiles) return;

    const fileObjs: { url: string; isImage: boolean; name: string; file: File }[] = [];
    Array.from(newFiles).forEach(file => {
      const url = URL.createObjectURL(file);
      const isImage = file.type.startsWith("image/");
      fileObjs.push({ url, isImage, name: file.name, file });
    });

    setFiles(prev => [...prev, ...fileObjs]);
  };

  const handleUploadFiles = async () => {
  try {
    if (files.length === 0) {
      console.log("No files to upload");
      return;
    }

    const formData = new FormData();
    files.forEach((fileObj) => {
      formData.append("files", fileObj.file);
    });
    
    const uploadEndpoint = `${queryUrl}/upload_files`;
    console.log("Uploading files to:", uploadEndpoint);

    const response = await fetch(uploadEndpoint, {
    method: "POST",
    body: formData,
    });

    if (!response.ok) {
      throw new Error("Failed to upload files");
    }

    const data = await response.json();
    console.log("Files uploaded:", data);
    alert("Files uploaded successfully!");

  } catch (error) {
    console.error("Error uploading files:", error);
    alert("Error uploading files");
  }
};

  

return (
  <div className="sql-editor-container h-full flex flex-col">
    <div
      className="sql-editor-header"
      style={{
        padding: '0.5rem',
        background: '#1e1e1e',
        borderBottom: '1px solid #2d3748',
      }}
    >
      <div className="flex items-center gap-2">
        <button
          className="editor-btn"
          onClick={() => onRun(localQuery)}
          disabled={isLoading || !localQuery.trim()}
          title={isLoading ? 'Query in progress...' : !localQuery.trim() ? 'Enter a query to run' : 'Run query'}
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            {isLoading ? <path d="M6 12h12M12 6v12" /> : <path d="M5 3l14 9-14 9V3z" />}
          </svg>
        </button>

        <button
          className="editor-btn"
          onClick={handleClear}
          disabled={isLoading}
          title="Clear editor"
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3-3h6M9 3v3M15 3v3M4 6h16" />
          </svg>
        </button>

      
        <button
            className="editor-btn"
            onClick={toggleEditor}
            title={showEditor ? 'Load files' : 'Edit query'}
            style={{
                minWidth: '120px',
                minHeight: '36px',
                marginLeft: '1rem',
                border: '1px solid #4a5568',
                borderRadius: '0.375rem',
            }}>

        {showEditor ? 'Load files' : 'Edit query'}
        </button>

        {!showEditor && (
        <button
            className="editor-btn"
            onClick={handleUploadFiles}
            title="Save content"
            style={{
            minWidth: '120px',
            minHeight: '36px',
            marginLeft: '1rem',
            border: '1px solid #4a5568',
            borderRadius: '0.375rem',
            }}
        >
            Save content
        </button>
        )}

        {copiedMessage && (
        <div
            style={{
            position: 'fixed',
            top: '1rem',
            right: '1rem',
            background: 'rgba(0, 0, 0, 0.8)',
            color: '#fff',
            padding: '0.5rem 1rem',
            borderRadius: '0.5rem',
            zIndex: 9999,
            fontSize: '14px',
            }}
        >
            {copiedMessage}
        </div>
        )}

      </div>
    </div>

    <div className="sql-editor-body flex-1" style={{ background: '#1e1e1e' }}>
      {showEditor ? (
        <CodeMirror
          value={localQuery}
          height="100%"
          extensions={[sql(), customHighlightPlugin, myTheme, syntaxHighlighting(myHighlightStyle)]}
          onChange={handleQueryChange}
          placeholder="Write your SQL query here..."
          style={{ fontSize: '14px', height: '100%' }}
        />
      ) : (
        <label
          className={`flex flex-col items-center justify-center h-full text-gray-300 gap-4 p-4 border-2 border-dashed rounded transition ${
            isDragging ? 'border-blue-400 bg-blue-900 bg-opacity-20' : 'border-gray-600'
          } ${files.length === 0 ? 'cursor-pointer' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          {files.length === 0 && (
            <>
              <span className="text-gray-300"
              style={{
                fontSize: '24px',
                color: isDragging ? '#38bdf8' : '#cbd5e1',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100%',
                width: '100%',
                }}
              
              >Click or drag files here</span>
              <input
                type="file"
                multiple
                onChange={handleFileChange}
                className="hidden"
              />
            </>
          )}

          <div
            className="flex flex-wrap justify-center gap-4 mt-4 p-2"
            style={{
                height: '100%',
                width: '100%',
                overflow: 'auto',
                scrollbarWidth: 'none',         // Firefox
                msOverflowStyle: 'none',        // IE y Edge
            }}
            >
            {files.map((file, idx) => (
              <div
  key={idx}
  className="flex flex-col items-center relative transition hover:opacity-80"
>
  {/* Botón X en la esquina */}
  <div
  onClick={(e) => {
    e.stopPropagation();
    handleRemoveFile(idx);
  }}
  style={{
    position: 'absolute',
    top: '4px',
    right: '4px',
    background: 'rgba(0,0,0,0.6)',
    color: '#fff',
    borderRadius: '50%',
    width: '24px',
    height: '24px',
    cursor: 'pointer',
    fontWeight: 'bold',
    lineHeight: '20px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    userSelect: 'none',
  }}
>
  ×
</div>

  <div
    onClick={() => handleCopyName(file.name)}
    
    style={{
      backgroundColor: 'rgba(6, 1, 29, 0.2)',
      borderRadius: '0.5rem',
      padding: '0.5rem',
      margin: '0.5rem',
      boxShadow: '0 1px 3px rgba(0,0,0,0.5)',
      width: '150px',
      height: '150px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      cursor: 'pointer',
      flexDirection: 'column',
    }}
  >
    {file.isImage ? (
      <>
        <img
          src={file.url}
          alt={file.name}
          className="max-w-[150px] max-h-[150px] rounded"
        />
        <span
          style={{
            wordBreak: 'break-all',
            textAlign: 'center',
            color: '#6e7486ff',
            fontFamily: 'JetBrains Mono, monospace',
            fontSize: '16px',
          }}
        >
          {file.name}
        </span>
      </>
    ) : (
      <div
        className="flex flex-col items-center justify-center w-[150px] h-[150px] bg-gray-800 rounded text-white text-xs p-2"
      >
        <img
          src={fileIcon}
          alt="File icon"
          className="mb-2 opacity-80"
          style={{ width: '64px', height: '64px', objectFit: 'contain' }}
        />
        <span
          style={{
            wordBreak: 'break-all',
            textAlign: 'center',
            color: '#5f6f83ff',
            fontFamily: 'JetBrains Mono, monospace',
            fontSize: '16px',
          }}
        >
          {file.name}
        </span>
      </div>
    )}
  </div>
</div>

            ))}
          </div>
        </label>
      )}
    </div>
  </div>
);
};

export default SQLEditor;
