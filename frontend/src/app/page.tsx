'use client'
import { useState, useRef, useEffect } from "react";
// import MarkdownRenderer from "./_components/MarkdownRenderer";
import styles from "./page.module.scss";

type RoleAndMessage = {
  role: 'ai' | 'user';
  content: string;
  think?: string;
};

export default function Home() {
  const [messages, setMessages] = useState<RoleAndMessage[] | []>([]);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const socket = useRef<WebSocket | null>(null);
  const aiMessageBuffer = useRef("")
  useEffect(() => {
    // socket.current = new WebSocket("ws://localhost:8000/ws");
    socket.current = new WebSocket("ws://localhost:8000/ws-decoy");
    socket.current.onmessage = (event) => {

      const text = event.data;
      console.log('Received chunk:', JSON.stringify(text));
      // console.log(text)
      setMessages((prevMsgs) => {
        const newMsgs = [...prevMsgs];
        const lastIndex = newMsgs.length - 1;
        aiMessageBuffer.current += text

        // If it's an AI continuation
        if (newMsgs[lastIndex]?.role === "ai") {
            newMsgs[lastIndex] = {
              ...newMsgs[lastIndex],
              content: aiMessageBuffer.current
            }
          }
        return newMsgs;
      });
    };

    return () => socket.current?.close();
  }, []);

  const sendMessage = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if(!input.trim()) return;
    const userMsg = { role: "user" as const, content: input };
    aiMessageBuffer.current = "";
    //setMessages and create a new placeholder for ai response
    setMessages((msgs) => [...msgs, userMsg, {role: "ai", content:""}]);
    socket.current?.send(input);
    setInput("")
  };

  return (
    <div className={styles.chatPageWrapper}>
      <div className={styles.chatContainer}>
        <div className={styles.chatWindow}>
          {messages.map((msg, i) =>
            msg.role === 'user' ?
              <div key={i} className={styles.userMessage}>{msg.content}</div> :
              <div key={i} className={styles.aiMessage}>{msg.content}</div>
          )}
          <div ref={messagesEndRef} />
        </div>
        <form className={styles.inputBar} onSubmit={sendMessage}>
          <input
            className={styles.input}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
          />
          <button className={styles.sendButton} type="submit">Send</button>
        </form>
      </div>
    </div>
  );
}