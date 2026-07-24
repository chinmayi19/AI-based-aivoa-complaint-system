import React, { useRef, useState } from "react";

export default function FileUpload({ onFile, disabled }) {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);

  const handleFiles = (files) => {
    if (files && files.length > 0) onFile(files[0]);
  };

  return (
    <div
      className={`dropzone ${dragging ? "dragging" : ""}`}
      onClick={() => !disabled && inputRef.current?.click()}
      onDragOver={(e) => {
        e.preventDefault();
        if (!disabled) setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        if (!disabled) handleFiles(e.dataTransfer.files);
      }}
    >
      <div className="dropzone-icon">☁️</div>
      <div className="dropzone-title">Drag &amp; drop complaint document here</div>
      <div>
        or <span className="dropzone-link">click to browse</span>
      </div>
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.docx,.txt,.eml"
        style={{ display: "none" }}
        disabled={disabled}
        onChange={(e) => handleFiles(e.target.files)}
      />
    </div>
  );
}
