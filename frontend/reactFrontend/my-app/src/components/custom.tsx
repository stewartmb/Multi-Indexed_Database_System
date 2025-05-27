import React, { useState } from "react";
import CodeMirror from "@uiw/react-codemirror";
import { sql } from "@codemirror/lang-sql";
import { EditorView, ViewPlugin, Decoration } from "@codemirror/view";
import type { ViewUpdate, DecorationSet } from "@codemirror/view";
import { HighlightStyle, syntaxHighlighting, tags as t } from "@codemirror/highlight";
import { RangeSetBuilder } from "@codemirror/state";

// 🎨 Palabras específicas y sus colores
const specialWords: Record<string, string> = {
  BPTREE: "#fb923c",
  SEQ: "#facc15",
  ISAM: "#f472b6",
  RLIKE: "#93c5fd",
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
      for (let { from, to } of view.visibleRanges) {
        const text = view.state.doc.sliceString(from, to);
        let match;
        while ((match = specialWordRegex.exec(text)) !== null) {
          const start = from + match.index;
          const end = start + match[0].length;
          const word = match[0].toUpperCase();
          const color = specialWords[word];
          if (!color) continue;
          const deco = Decoration.mark({
            attributes: { style: `color: ${color}; font-weight: bold` }
          });
          builder.add(start, end, deco);
        }
      }
      return builder.finish();
    }
  },
  {
    decorations: v => v.decorations
  }
);