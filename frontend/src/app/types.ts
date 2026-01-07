export type RoleAndMessage = {
  role: 'ai' | 'user';
  content: string;
  think?: string;
  sources?: { url: string; domain: string; favicon: string }[];
};

export type EditablePromptInputBarProps = {
  input: string;
  setInput: React.Dispatch<React.SetStateAction<string>>;
  onSendMessage: () => void;
};
