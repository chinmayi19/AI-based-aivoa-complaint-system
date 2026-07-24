import React, { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import FileUpload from "./FileUpload";
import ChatBox from "./ChatBox";
import { setFields, setAiInsights, setSourceDocumentName } from "../store/complaintSlice";
import { addMessage, setProgress, setExtracting, setChatting } from "../store/chatSlice";
import { extractFromFile, extractFromText, sendChatMessage } from "../api/client";

export default function AIAssistantPanel() {
  const dispatch = useDispatch();
  const { sessionId, messages, progressPercent, progressLabel, isExtracting, isChatting } = useSelector((s) => s.chat);
  const fields = useSelector((s) => s.complaint.fields);
  const aiInsights = useSelector((s) => s.complaint.aiInsights);

  const [showPasteBox, setShowPasteBox] = useState(false);
  const [pastedText, setPastedText] = useState("");
  const [chatInput, setChatInput] = useState("");
  const [error, setError] = useState(null);

  const applyExtractionResult = (result, sourceName) => {
    dispatch(setFields(result.extracted_fields || {}));
    dispatch(setSourceDocumentName(sourceName));
    dispatch(
      setAiInsights({
        completeness_score: result.completeness_score,
        missing_fields: result.missing_fields,
        risk_classification: result.risk_classification,
        risk_rationale: result.risk_rationale,
        ai_summary: result.ai_summary,
        root_cause_suggestion: result.root_cause_suggestion,
        capa_recommendation: result.capa_recommendation,
        duplicate_warning: result.duplicate_warning,
      })
    );
    dispatch(setProgress({ percent: 100, label: "Extraction complete." }));
    dispatch(addMessage({ role: "assistant", content: result.assistant_message }));
  };

  const runExtraction = async (fn, sourceName) => {
    setError(null);
    dispatch(setExtracting(true));
    try {
      // Simulated staged progress while the LangGraph pipeline runs server-side
      const stages = [
        [25, "Extracting structured fields with Groq (gemma2-9b-it)..."],
        [50, "Checking record completeness..."],
        [70, "Running AI risk classification..."],
        [90, "Generating summary and CAPA recommendation..."],
      ];
      let i = 0;
      const timer = setInterval(() => {
        if (i < stages.length) {
          const [percent, label] = stages[i];
          dispatch(setProgress({ percent, label }));
          i += 1;
        }
      }, 500);

      const result = await fn();
      clearInterval(timer);
      applyExtractionResult(result, sourceName);
    } catch (err) {
      setError(err?.response?.data?.detail || "Extraction failed. Please check the backend/Groq API key and try again.");
      dispatch(setProgress({ percent: 0, label: "" }));
    } finally {
      dispatch(setExtracting(false));
    }
  };

  const handleFile = (file) => {
    runExtraction(() => extractFromFile(file, sessionId), file.name);
  };

  const handlePasteSubmit = () => {
    if (!pastedText.trim()) return;
    runExtraction(() => extractFromText(pastedText, sessionId), "Pasted text");
    setShowPasteBox(false);
    setPastedText("");
  };

  const handleChatSend = async () => {
    if (!chatInput.trim() || isChatting) return;
    const userMsg = chatInput.trim();
    setChatInput("");
    dispatch(addMessage({ role: "user", content: userMsg }));
    dispatch(setChatting(true));
    try {
      const result = await sendChatMessage(sessionId, userMsg, fields);
      dispatch(addMessage({ role: "assistant", content: result.assistant_message }));
      if (result.updated_fields && Object.keys(result.updated_fields).length > 0) {
        dispatch(setFields(result.updated_fields));
      }
    } catch (err) {
      dispatch(addMessage({ role: "assistant", content: "Sorry, I ran into an error reaching the assistant. Please try again." }));
    } finally {
      dispatch(setChatting(false));
    }
  };

  const disabled = isExtracting;

  return (
    <div className="card assistant-panel">
      <div className="assistant-header">
        <div className="assistant-header-title">✨ AI Complaint Intake Assistant</div>
        <span className="beta-badge">BETA</span>
      </div>

      <div className="assistant-body">
        <FileUpload onFile={handleFile} disabled={disabled} />

        <div className="divider-or">OR</div>

        {!showPasteBox ? (
          <button className="paste-btn" onClick={() => setShowPasteBox(true)} disabled={disabled}>
            📄 Paste Complaint Text / Email
          </button>
        ) : (
          <div className="paste-textarea-wrap">
            <textarea
              autoFocus
              placeholder="Paste the complaint email or document text here..."
              value={pastedText}
              onChange={(e) => setPastedText(e.target.value)}
            />
            <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
              <button className="btn btn-primary" onClick={handlePasteSubmit} disabled={disabled}>
                Extract Details
              </button>
              <button className="btn btn-ghost" onClick={() => setShowPasteBox(false)} disabled={disabled}>
                Cancel
              </button>
            </div>
          </div>
        )}

        <div className="support-note">
          ℹ️ Supported formats: PDF, DOCX, TXT, EML. Max file size: 10MB
        </div>

        {(isExtracting || progressPercent > 0) && (
          <div>
            <div className="progress-section-label">
              <span>EXTRACTION PROGRESS</span>
              <span>{progressPercent}%</span>
            </div>
            <div className="progress-track">
              <div className="progress-fill" style={{ width: `${progressPercent}%` }} />
            </div>
            <div className="progress-caption">{progressLabel}</div>
          </div>
        )}

        {error && <div className="duplicate-banner">⚠️ {error}</div>}

        {aiInsights.duplicate_warning && (
          <div className="duplicate-banner">
            ⚠️ Possible duplicate: {aiInsights.duplicate_warning.duplicate_summary}
          </div>
        )}

        {(aiInsights.completeness_score !== null || aiInsights.risk_classification) && (
          <div className="ai-insights">
            {aiInsights.completeness_score !== null && (
              <div className="insight-card">
                <div className="insight-card-title">
                  <span>Completeness Check</span>
                  <span>{aiInsights.completeness_score}%</span>
                </div>
                {aiInsights.missing_fields?.length > 0
                  ? `Missing/weak fields: ${aiInsights.missing_fields.join(", ")}`
                  : "All required fields look present."}
              </div>
            )}
            {aiInsights.risk_classification && (
              <div className="insight-card">
                <div className="insight-card-title">
                  <span>AI Risk Classification</span>
                  <span className={`risk-pill ${aiInsights.risk_classification}`}>{aiInsights.risk_classification}</span>
                </div>
                {aiInsights.risk_rationale}
              </div>
            )}
            {aiInsights.ai_summary && (
              <div className="insight-card">
                <div className="insight-card-title"><span>Complaint Summary</span></div>
                {aiInsights.ai_summary}
              </div>
            )}
            {aiInsights.root_cause_suggestion && (
              <div className="insight-card">
                <div className="insight-card-title"><span>Root Cause Suggestion</span></div>
                {aiInsights.root_cause_suggestion}
              </div>
            )}
            {aiInsights.capa_recommendation && (
              <div className="insight-card">
                <div className="insight-card-title"><span>CAPA Recommendation</span></div>
                {aiInsights.capa_recommendation}
              </div>
            )}
          </div>
        )}

        <div>
          <div className="progress-section-label">
            <span>AI ASSISTANT</span>
          </div>
          <ChatBox messages={messages} />
        </div>

        <div className="chat-input-row">
          <input
            placeholder="Ask me anything about this complaint..."
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleChatSend()}
            disabled={isChatting}
          />
          <button className="chat-send-btn" onClick={handleChatSend} disabled={isChatting || !chatInput.trim()}>
            ➤
          </button>
        </div>
        <div className="disclaimer">All responses may contain errors. Please verify information.</div>
      </div>
    </div>
  );
}
