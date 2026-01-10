import { useState, useEffect } from 'react';
import styles from '../page.module.scss';
import { createPortal } from 'react-dom';

interface LoginModalProps {
  onLogin: (username: string) => void;
}

export default function LoginModal({ onLogin }: LoginModalProps) {
  const [username, setUsername] = useState('');
  const [error, setError] = useState('');
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = username.trim();
    
    // Validation: simple lowercase alphanumeric
    // "using only lowercase letters and no symbols" -> ^[a-z0-9]+$ allows numbers too which is safer for IDs
    if (!/^[a-z0-9]+$/.test(trimmed)) {
      setError('Username must be lowercase letters and numbers only (no spaces or symbols).');
      return;
    }
    
    if (trimmed.length < 3) {
      setError('Username must be at least 3 characters long.');
      return;
    }

    onLogin(trimmed);
  };

  if (!mounted) return null;

  // Simple modal using fixed positioning (or portal if preferred, but fixed is easiest for quick drop-in)
  return createPortal(
    <div className={styles.modalOverlay}>
      <div className={styles.modalContent}>
        <h2>Welcome to Yeti Agent</h2>
        <p>Please enter a username to continue. This will be used to save your chat history.</p>
        
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            className={styles.loginInput}
            placeholder="username (e.g. alice)"
            value={username}
            onChange={(e) => {
              setUsername(e.target.value.toLowerCase());
              setError('');
            }}
            autoFocus
          />
          {error && <p className={styles.errorMessage}>{error}</p>}
          <button type="submit" className={styles.loginButton} disabled={!username}>
            Start Chatting
          </button>
        </form>
      </div>
    </div>,
    document.body
  );
}
