'use client'
import { useState, useRef, useEffect } from "react";
import MarkdownRenderer from "./_components/MarkdownRenderer";
import styles from "./page.module.scss";
import { RoleAndMessage, EditablePromptInputBarProps } from './types';

function useChat() {
  const [messages, setMessages] = useState<RoleAndMessage[] | []>([]);
  const [input, setInput] = useState("");
  const [status, setStatus] = useState(""); // status text (thinking/searching)
  const [isBusy, setIsBusy] = useState(false); // UI lock state
  const socket = useRef<WebSocket | null>(null);
  const aiMessageBuffer = useRef("");
  const chunk_ = useRef("");

  useEffect(() => {
    // 1. Fetch history from backend on mount
    const fetchHistory = async () => {
      try {
        const response = await fetch("http://localhost:8000/api/history?thread_id=1");
        if (!response.ok) throw new Error("Failed to fetch history");
        const data = await response.json();
        if (data.messages && data.messages.length > 0) {
          console.log(`📜 Loaded ${data.messages.length} messages from history`);
          setMessages(data.messages);
        }
      } catch (err) {
        console.error("❌ Error loading history:", err);
      }
    };

    fetchHistory();

    // 2. Setup WebSocket
    socket.current = new WebSocket("ws://localhost:8000/ws");

    socket.current.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);

        if (payload.type === "signal") {
          if (payload.status === "ready") {
            setIsBusy(false);
            // Only clear the status if it's not a completion message
            setStatus((prev) =>
              prev.toLowerCase().includes("finish") || prev.toLowerCase().includes("complete")
                ? prev
                : ""
            );
          } else {
            // Prefer the dynamic message from backend, fallback to status code
            setStatus(payload.message || payload.status);

            // If sources are provided, update the last AI message
            if (payload.sources && payload.sources.length > 0) {
              setMessages((prevMsgs) => {
                const newMsgs = [...prevMsgs];
                const lastIndex = newMsgs.length - 1;
                if (newMsgs[lastIndex]?.role === "ai") {
                  newMsgs[lastIndex] = {
                    ...newMsgs[lastIndex],
                    sources: payload.sources
                  };
                }
                return newMsgs;
              });
            }
          }
          return;
        }

        if (payload.type === "chunk") {
          setStatus(""); // Clear status text when content starts
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
        setIsBusy(false);
      }
    };

    return () => socket.current?.close();
  }, []);

  const sendMessage = async (e?: React.FormEvent, manualMessage?: string) => {
    if (e) e.preventDefault();
    const messageToSend = manualMessage !== undefined ? manualMessage : input;
    if (!messageToSend.trim()) return;

    setIsBusy(true); // Lock UI
    const userMsg = { role: "user" as const, content: messageToSend, think: "" };
    aiMessageBuffer.current = "";
    setStatus("thinking");
    setMessages((msgs) => [...msgs, userMsg, { role: "ai", content: "", think: "", sources: [] }]);
    socket.current?.send(messageToSend);
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

  const addMessage = (role: "user" | "ai", content: string, think: string = "") => {
    setMessages((msgs) => [...msgs, { role, content, think }]);
  };

  return { messages, input, setInput, sendMessage, status, addMessage, setStatus, isBusy, setIsBusy };
}

function EditablePromptInputBar({ input, setInput, onSendMessage, disabled }: EditablePromptInputBarProps & { disabled?: boolean }) {
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
    if (!disabled && (event.metaKey || event.ctrlKey) && event.key === "Enter") {
      event.preventDefault();
      onSendMessage();
    }
  };

  return (
    <div
      ref={editableRef}
      className={`${styles.editablePromptInputBar} ${!input ? styles.empty : ""} ${disabled ? styles.disabled : ""}`}
      contentEditable={!disabled}
      onInput={handleInput}
      onKeyDown={handleKeyDown}
      suppressContentEditableWarning={true}
      data-placeholder={disabled ? "Please wait..." : "Type your message..."}
    />
  );
}

function ChatWindow({ messages, status }: { messages: RoleAndMessage[]; status: string }) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, status]);

  const getStatusMessage = (status: string) => {
    // These are fallback messages for internal status codes
    const fallbacks: Record<string, string> = {
      searching: "Yeti is scouring the valleys...",
      thinking: "Yeti is meditating on the glaciers...",
    };

    // If the status matches a fallback key, use it. 
    // Otherwise, assume 'status' is already the descriptive message from the backend.
    return fallbacks[status] || status || "Yeti is working...";
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
            {msg.content && <MarkdownRenderer content={msg.content} />}

            {/* Show search sources if available */}
            {msg.sources && msg.sources.length > 0 && (
              <div className={styles.sourceContainer}>
                <p className={styles.sourceHeader}>Sources found:</p>
                <div className={styles.sourceList}>
                  {msg.sources.map((source, idx) => (
                    <a key={idx} href={source.url} target="_blank" rel="noopener noreferrer" className={styles.sourceItem}>
                      <img src={source.favicon} alt="" className={styles.favicon} />
                      <span className={styles.domain}>{source.domain}</span>
                    </a>
                  ))}
                </div>
              </div>
            )}

            {/* Show status if it's the latest message */}
            {i === messages.length - 1 && status && (
              <div className={styles.statusIndicator}>
                {/* Hide spinner for completion messages */}
                {!(status.toLowerCase().includes("finish") || status.toLowerCase().includes("complete")) && (
                  <span className={styles.spinner}></span>
                )}
                <span className={styles.statusText}>{getStatusMessage(status)}</span>
              </div>
            )}
          </div>
        )
      )}
      <div ref={messagesEndRef} />
    </div>
  );
}

export default function Home() {
  const chatHook = useChat();
  const { messages, input, setInput, sendMessage, status, isBusy, setIsBusy, addMessage, setStatus } = chatHook;

  const handleShortcut = async (type: string) => {
    if (isBusy) return;

    let prompt = "";

    switch (type) {
      case "rate":
        prompt = "What is the current JPY to INR exchange rate?";
        break;
      case "weather":
        prompt = "What is the current weather in Tokyo?";
        break;
      case "time":
        prompt = "What is the current time?";
        break;
      case "search":
        prompt = "Look up Digital Wallet Corporation on the internet.";
        break;
      case "shipton":
        prompt = "Tell me about your first encounter with Shipton.";
        break;
      case "introduction":
        prompt = "I am preparing your for a demo to my company's executives. So When I ask you to introduce yourself, please provide an introduction, and greet the following people: Mr. Eiji Miyakawa (CEO), Mr. Takeru Kaneko(CTO), and Mr. Kawachi Tsutomu (R&D Head). Let them know you are working hard to impress them with our capabilites. Also apologize for the delay in response due to current hardware limitations. Respond in Markdown format, highlight names of executives and the company name. List the tools you have at your disposal. And explain the capabilities of each tool in bullets. Explain your design philosophy and how you plan to use the tools. In the last paragraph, share your personal story of how you moved from Everest to Fuji, and your experiences.";
        break;
    }

    if (!prompt) return;

    // Route through the agent (WebSocket)
    setInput(prompt);
    // Send directly to avoid state update race conditions
    sendMessage(undefined, prompt);
  };

  return (
    <div className={styles.chatPageWrapper}>
      <div className={styles.chatContainer}>
        <ChatWindow messages={messages} status={status} />

        <div className={styles.inputArea}>
          <div className={styles.shortcutContainer}>
            <button disabled={isBusy} className={styles.shortcutButton} onClick={() => handleShortcut("introduction")}>
              👣 Introduction
            </button>
            <button disabled={isBusy} className={styles.shortcutButton} onClick={() => handleShortcut("rate")}>
              💴 JPY to INR
            </button>
            <button disabled={isBusy} className={styles.shortcutButton} onClick={() => handleShortcut("weather")}>
              🌤️ Tokyo Weather
            </button>
            <button disabled={isBusy} className={styles.shortcutButton} onClick={() => handleShortcut("time")}>
              🕒 Time
            </button>
            <button disabled={isBusy} className={styles.shortcutButton} onClick={() => handleShortcut("search")}>
              🔍 Search DWC
            </button>
            <button disabled={isBusy} className={styles.shortcutButton} onClick={() => handleShortcut("shipton")}>
              👣 First Encounter
            </button>
          </div>

          <div className={styles.inputRow}>
            <EditablePromptInputBar
              input={input}
              setInput={setInput}
              onSendMessage={sendMessage}
              disabled={isBusy}
            />
            <button
              className={styles.sendButton}
              type="submit"
              onClick={sendMessage}
              disabled={isBusy}
            >
              Send
            </button>
          </div>
        </div>
        <div className={styles.disclaimer}>
          AI can make mistakes, just like humans. Please do your own verification.
        </div>
      </div>
    </div>
  );
}

