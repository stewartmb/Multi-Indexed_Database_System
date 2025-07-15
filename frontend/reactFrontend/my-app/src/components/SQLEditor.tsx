import React, { useState, useEffect } from 'react';
import CodeMirror from '@uiw/react-codemirror';
import { sql } from '@codemirror/lang-sql';
import { EditorView, ViewPlugin, Decoration } from "@codemirror/view";
import { HighlightStyle, syntaxHighlighting } from '@codemirror/language';
import { tags as t } from '@lezer/highlight';
import { useQueryUrl } from '../contexts/QueryUrlContext.tsx';
import {completeFromList} from "@codemirror/autocomplete";

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
  const { queryUrl, setQueryUrl } = useQueryUrl();
  const [images, setImages] = useState<string[]>([]);
  const [isDragging, setIsDragging] = useState(false);

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
  const files = e.target.files;
  if (!files) return;

  const newImages: string[] = [];
  Array.from(files).forEach(file => {
    const url = URL.createObjectURL(file);
    newImages.push(url);
  });

  setImages(prev => [...prev, ...newImages]);
};

const handleRemoveImage = (index: number) => {
  setImages(prev => {
    URL.revokeObjectURL(prev[index]);
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

  const files = e.dataTransfer.files;
  if (!files) return;

  const newImages: string[] = [];
  Array.from(files).forEach(file => {
    const url = URL.createObjectURL(file);
    newImages.push(url);
  });

  setImages(prev => [...prev, ...newImages]);
};


  return (
    <div className="sql-editor-container h-full flex flex-col">
      <div className="sql-editor-header" style={{
        padding: '0.5rem',
        background: '#1e1e1e',
        borderBottom: '1px solid #2d3748'
      }}>
        <div className="flex items-center gap-2">
          <button
            className="editor-btn"
            onClick={() => onRun(localQuery)}
            disabled={isLoading || !localQuery.trim()}
            title={isLoading ? 'Query in progress...' : !localQuery.trim() ? 'Enter a query to run' : 'Run query'}
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              {isLoading ? (
                <path d="M6 12h12M12 6v12" />
              ) : (
                <path d="M5 3l14 9-14 9V3z" />
              )}
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
          >
            {showEditor ? 'Load files' : 'Edit query'}
          </button>
        </div>
      </div>

      <div className="sql-editor-body flex-1" style={{ background: '#1e1e1e' }}>
        {showEditor ? (
          <CodeMirror 
            value={localQuery}
            height="100%"
            extensions={[
              sql(),
              customHighlightPlugin,
              myTheme,
              syntaxHighlighting(myHighlightStyle),
            ]}
            onChange={handleQueryChange}
            placeholder="Write your SQL query here..."
            style={{
              fontSize: '14px',
              height: '100%'
            }}
          />
        ) : (
            <div
                className={`flex flex-col items-center justify-center h-full text-gray-400 gap-4 p-4 border-2 border-dashed rounded transition 
                    ${isDragging ? 'border-blue-400 bg-blue-900 bg-opacity-20' : 'border-gray-600'}`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                >
                <label className="cursor-pointer bg-gray-700 px-4 py-2 rounded hover:bg-gray-600">
                    Select images
                    <input
                    type="file"
                    accept="image/*"
                    multiple
                    onChange={handleFileChange}
                    className="hidden"
                    />
                </label>

                <div className="flex flex-wrap justify-center gap-4 mt-4">
                    {images.map((src, idx) => (
                    <img
                        key={idx}
                        src={src}
                        alt={`Preview ${idx}`}
                        className="max-w-[150px] max-h-[150px] rounded shadow cursor-pointer hover:opacity-70 transition"
                        onClick={() => handleRemoveImage(idx)}
                    />
                    ))}
                </div>
            </div>
        )}
      </div>
    </div>
  );
};

export default SQLEditor;
