import React, { useEffect, useRef } from "react";

export default function ChatBox({ messages }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="assistant-messages">
      {messages.map((m) => (
        <div key={m.id} className={`chat-bubble ${m.role}`}>
          <div className={`chat-avatar ${m.role}`}>{m.role === "assistant" ? "✨" : "🙂"}</div>
          <div className="chat-text">{m.content}</div>
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
