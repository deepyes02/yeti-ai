'use client'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import 'highlight.js/styles/github-dark.css'
import styles from "./MarkdownRenderer.module.scss"
// import "../global.scss"

export default function MarkdownRenderer({ content }: { content: string }) {
  return ( 
    <div className={styles.markdownContainer}><ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeHighlight]}>{content}</ReactMarkdown></div>
  );
}

