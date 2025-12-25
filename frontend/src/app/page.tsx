'use client'
import { useState, useRef, useEffect } from "react";
import MarkdownRenderer from "./_components/MarkdownRenderer";
import styles from "./page.module.scss";
import { RoleAndMessage, EditablePromptInputBarProps } from './types';

function useChat() {
  const [messages, setMessages] = useState<RoleAndMessage[] | []>([]);
  const [input, setInput] = useState("");
  const [status, setStatus] = useState("");
  const socket = useRef<WebSocket | null>(null);
  const aiMessageBuffer = useRef("");
  const chunk_ = useRef("");

  useEffect(() => {
    socket.current = new WebSocket("ws://localhost:8000/ws");

    socket.current.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        
        if (payload.type === "signal") {
          setStatus(payload.status);
          return;
        }

        if (payload.type === "chunk") {
          setStatus(""); // Clear status when content starts
          const text = payload.data;
          setMessages((prevMsgs) => {
            const newMsgs = [...prevMsgs];
            const lastIndex = newMsgs.length - 1;
            aiMessageBuffer.current += text;
            chunk_.current += text;
            const { think, content } = splitThinkAndContent(chunk_.current);

            if (newMsgs[lastIndex]?.role === "ai") {
              newMsgs[lastIndex] = {
                ...newMsgs[lastIndex],
                content: content,
                think: think,
              };
            }
            return newMsgs;
          });
        }
      } catch (e) {
        console.error("Error parsing websocket message", e);
      }
    };

    return () => socket.current?.close();
  }, []);

  const sendMessage = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim()) return;
    const userMsg = { role: "user" as const, content: input, think: "" };
    aiMessageBuffer.current = "";
    setStatus("thinking"); // Initial status
    setMessages((msgs) => [...msgs, userMsg, { role: "ai", content: "", think: "" }]);
    socket.current?.send(input);
    setInput("");
    chunk_.current = "";
  };

  function splitThinkAndContent(text: string) {
    const match = text.match(/<think>([\s\S]*?)<\/think>/);
    if (match) {
      const think = match[1];
      const content = text.slice((match.index ?? 0) + match[0].length);
      return { think, content };
    } else {
      return { think: "", content: text };
    }
  }

  return { messages, input, setInput, sendMessage, status };
}

function EditablePromptInputBar({ input, setInput, onSendMessage }: EditablePromptInputBarProps) {
  const editableRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (editableRef.current && input === "") {
      editableRef.current.innerHTML = "";
    }
  }, [input]);

  const handleInput = () => {
    const text = editableRef.current?.innerText;
    setInput(text ?? "");
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
    if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
      event.preventDefault();
      onSendMessage();
    }
  };

  return (
    <div
      ref={editableRef}
      className={`${styles.editablePromptInputBar} ${!input ? styles.empty : ""}`}
      contentEditable
      onInput={handleInput}
      onKeyDown={handleKeyDown}
      suppressContentEditableWarning={true}
      data-placeholder="Type your message..."
    />
  );
}

function ChatWindow({ messages, status }: { messages: RoleAndMessage[]; status: string }) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, status]);

  const getStatusMessage = (status: string) => {
    switch (status) {
      case "searching":
        return "Yeti is scouring the valleys...";
      case "thinking":
        return "Yeti is meditating on the glaciers...";
      default:
        return "Yeti is working...";
    }
  };

  return (
    <div className={styles.chatWindow}>
      {messages.map((msg, i) =>
        msg.role === "user" ? (
          <div key={i} className={styles.userMessage}>
            {msg.content}
          </div>
        ) : (
          <div className={styles.aiResponseBox} key={i}>
            {msg.think && (
              <div className={styles.thinkMessage}>
                <p>{msg.think}</p>
              </div>
            )}
            {msg.content ? (
              <MarkdownRenderer content={msg.content} />
            ) : (
              i === messages.length - 1 &&
              status && (
                <div className={styles.statusIndicator}>
                  <span className={styles.spinner}></span>
                  {getStatusMessage(status)}
                </div>
              )
            )}
          </div>
        )
      )}
      <div ref={messagesEndRef} />
    </div>
  );
}

export default function Home() {
  const { messages, input, setInput, sendMessage, status } = useChat();

  return (
    <div className={styles.chatPageWrapper}>
      <div className={styles.chatContainer}>
        <ChatWindow messages={messages} status={status} />
        <div className={styles.inputWrapper}>
          <EditablePromptInputBar
            input={input}
            setInput={setInput}
            onSendMessage={sendMessage}
          />
          <button
            className={styles.sendButton}
            type="submit"
            onClick={sendMessage}
          >
            Send
          </button>
        </div>
        <div className={styles.disclaimer}>
          AI can make mistakes, so always verify the information it provides. Ask about weather, exchange rates, current date and time, and search the web for information. You can also ask it to think about a problem before answering.
        </div>
      </div>
    </div>
  );
}

