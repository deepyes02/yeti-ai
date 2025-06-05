'use client'
import { useState, useRef, useEffect } from "react";
import styles from "./page.module.scss";

export default function Home() {
  const [messages, setMessages] = useState([
    { role: "ai", content: "Hello! How can I help you today?" },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const socket = useRef<WebSocket | null>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
  socket.current = new WebSocket("ws://localhost:8000/ws");

  socket.current.onmessage = (event) => {
    const text = event.data;
    setMessages((prev) => {
      const newMsgs = [...prev];
      if (newMsgs[newMsgs.length - 1]?.content === "...") {
        newMsgs[newMsgs.length - 1].content = text;
      } else {
        newMsgs.push({ role: "ai", content: text });
      }
      return newMsgs;
    });
  };

  return () => socket.current?.close();
}, []);

  const sendMessage = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim()) return;
    const userMsg = { role: "user", content: input };
    setMessages((msgs) => [...msgs, userMsg]);
    setInput("");
    setLoading(true);
    setMessages((msgs) => [
      ...msgs, userMsg,
      { role: "ai", content: "..." },
    ]);
    socket.current?.send(input);
    setInput('')
  };

  return (
    <div className={styles.chatPageWrapper}>
      <div className={styles.chatContainer}>
        <div className={styles.chatWindow}>
          {messages.map((msg, i) => (
            <div
              key={i}
              className={
                msg.role === "user"
                  ? styles.userMessage
                  : styles.aiMessage
              }
            >
              {msg.content}
            </div>
          ))}
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
          {!loading && <button className={styles.sendButton} type="submit">Send</button>}
        </form>
      </div>
    </div>
  );
}