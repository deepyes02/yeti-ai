'use client'
import { useState, useRef, useEffect } from "react";
import styles from "./page.module.scss";

export default function Home() {
  const [messages, setMessages] = useState([
    { role: "ai", content: "Hello! How can I help you today?" },
  ]);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim()) return;
    const userMsg = { role: "user", content: input };
    setMessages((msgs) => [...msgs, userMsg]);
    setInput("");
    // Placeholder for API call
    setTimeout(() => {
      setMessages((msgs) => [
        ...msgs,
        { role: "ai", content: "(AI response placeholder)" },
      ]);
    }, 800);
  };

  return (
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
        <button className={styles.sendButton} type="submit">
          Send
        </button>
      </form>
    </div>
  );
}