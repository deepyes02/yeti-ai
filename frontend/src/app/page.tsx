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
    fetch('/api/chat').then(res=>res.json().then(data=>{console.log(data)}))
    // fetch('http://localhost:8000').then(res=>res.json().then(data=>{console.log(data)}))

  }, [messages]);

const sendMessage = async (e?: React.FormEvent) => {
  if (e) e.preventDefault();
  if (!input.trim()) return;
  const userMsg = { role: "user", content: input };
  setMessages((msgs) => [...msgs, userMsg]);
  const prompt = input;
  setInput("");
  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt }),
    });
    const data = await res.json();
    setMessages((msgs) => [
      ...msgs,
      { role: "ai", content: data.response || "(No response)" },
    ]);
  } catch (err) {
    setMessages((msgs) => [
      ...msgs,
      { role: "ai", content: "(Error contacting AI)" },
    ]);
  }
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
        <button className={styles.sendButton} type="submit">
          Send
        </button>
      </form>
    </div>
    </div>
  );
}