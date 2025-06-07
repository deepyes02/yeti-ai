// components/MarkdownRenderer.tsx
'use client'

import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
// import rehypeRaw from "rehype-raw";
import rehypeHighlight from 'rehype-highlight'
import 'highlight.js/styles/github.css' // choose any style from highlight.js
import "../globals.scss"

export default function MarkdownRenderer({ content }: { content: string }) {
  return (
    <div className="prose max-w-none dark:prose-invert">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[ rehypeHighlight]}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}