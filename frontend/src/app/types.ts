export type RoleAndMessage = {
  role: 'ai' | 'user';
  content: string;
  think?: string;
};

export type EditablePromptInputBarProps = {
  input: string;
  setInput: React.Dispatch<React.SetStateAction<string>>;
  onSendMessage: () => void;
};
