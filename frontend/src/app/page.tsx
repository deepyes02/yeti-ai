'use client'
import { useState, useRef, useEffect } from "react";
import MarkdownRenderer from "./_components/MarkdownRenderer";
import styles from "./page.module.scss";

type RoleAndMessage = {
  role: 'ai' | 'user';
  content: string;
  think?: string;
};

type EditablePromptInputBarProps = {
  input: string;
  setInput: React.Dispatch<React.SetStateAction<string>>;
};

function EditablePromptInputBar({ input, setInput }: EditablePromptInputBarProps) {
  const editableRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (editableRef.current && input === '') {
      editableRef.current.innerHTML = ''; // clear if input is empty
    }
  }, [input]);


  const handleInput = () => {
    const text = editableRef.current?.innerText;
    setInput(text ?? "");
  };

  return (
    <div
      ref={editableRef}
      className={`${styles.editablePromptInputBar} ${!input ? styles.empty : ''}`}
      contentEditable
      onInput={handleInput}
      suppressContentEditableWarning={true}
      data-placeholder="Type your message..."
    />
  );
}

export default function Home() {
  const [messages, setMessages] = useState<RoleAndMessage[] | []>([]);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const socket = useRef<WebSocket | null>(null);
  const aiMessageBuffer = useRef("")
  const chunk_ = useRef("")

  useEffect(() => {
    socket.current = new WebSocket("ws://localhost:8000/ws");
    // socket.current = new WebSocket("ws://localhost:8000/ws-decoy");
    socket.current.onmessage = (event) => {
      const text = event.data;
      setMessages((prevMsgs) => {
        const newMsgs = [...prevMsgs];
        const lastIndex = newMsgs.length - 1;
        aiMessageBuffer.current += text
        chunk_.current += text
        // console.log(splitThinkAndContent(chunk_.current))
        const { think, content } = splitThinkAndContent(chunk_.current);

        // If it's an AI continuation
        if (newMsgs[lastIndex]?.role === "ai") {
          newMsgs[lastIndex] = {
            ...newMsgs[lastIndex],
            content: content,
            think: think
          }
        }
        return newMsgs;
      });
    };

    return () => socket.current?.close();
  }, []);

  const sendMessage = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim()) return;
    const userMsg = { role: "user" as const, content: input, think: '' };
    aiMessageBuffer.current = "";
    //setMessages and create a new placeholder for ai response
    setMessages((msgs) => [...msgs, userMsg, { role: "ai", content: "", think: '' }]);
    socket.current?.send(input);
    setInput("")
    chunk_.current = '';
  };
  function splitThinkAndContent(text: string) {
    const match = text.match(/<think>([\s\S]*?)<\/think>/);
    if (match) {
      const think = match[1]; // content inside <think>
      const content = text.slice((match.index ?? 0) + match[0].length); // everything after </think>
      return { think, content };
    } else {
      return { think: "", content: text }; // no <think> block found
    }
  }


  return (
    <div className={styles.chatPageWrapper}>
      <div className={styles.chatContainer}>
        <div className={styles.chatWindow}>
          {messages.map((msg, i) =>
            msg.role === 'user' ?
              <div key={i} className={styles.userMessage}>{msg.content}</div> :
              <div className={styles.aiResponseBox} key={i}>
                {msg.think && <div className={styles.thinkMessage}><p>{msg.think}</p></div>}
                {msg.content && <MarkdownRenderer content={msg.content} />}
              </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        <div className={styles.inputWrapper}>
          <EditablePromptInputBar input={input} setInput={setInput} />
          <button
            className={styles.sendButton}
            type="submit"
            onClick={sendMessage}
          >
            Send
          </button>
        </div>

      </div>
    </div>
  );
}
