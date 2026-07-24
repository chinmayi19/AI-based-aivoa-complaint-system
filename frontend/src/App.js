import React, { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import ComplaintForm from "./components/ComplaintForm";
import AIAssistantPanel from "./components/AIAssistantPanel";
import ComplaintsListPage from "./components/ComplaintsListPage";
import { createComplaint, updateComplaint, attachAiResults } from "./api/client";
import { setSavedId, setSaveState, resetForm } from "./store/complaintSlice";
import { resetSession } from "./store/chatSlice";

export default function App() {
  const [tab, setTab] = useState("new"); // "new" | "list"
  const [toast, setToast] = useState(null);
  const dispatch = useDispatch();

  const fields = useSelector((s) => s.complaint.fields);
  const savedId = useSelector((s) => s.complaint.savedId);
  const saveState = useSelector((s) => s.complaint.saveState);
  const aiInsights = useSelector((s) => s.complaint.aiInsights);

  const showToast = (msg) => {
    setToast(msg);
    setTimeout(() => setToast(null), 3000);
  };

  const handleSave = async () => {
    dispatch(setSaveState("saving"));
    try {
      let complaint;
      if (savedId) {
        complaint = await updateComplaint(savedId, fields);
      } else {
        complaint = await createComplaint(fields);
        dispatch(setSavedId(complaint.id));
      }
      // Attach whatever AI analysis has been generated for this session
      if (aiInsights.completeness_score !== null || aiInsights.risk_classification) {
        await attachAiResults(complaint.id, {
          session_id: "n/a",
          extracted_fields: fields,
          progress_log: [],
          assistant_message: "",
          completeness_score: aiInsights.completeness_score,
          missing_fields: aiInsights.missing_fields || [],
          risk_classification: aiInsights.risk_classification,
          risk_rationale: aiInsights.risk_rationale,
          ai_summary: aiInsights.ai_summary,
          root_cause_suggestion: aiInsights.root_cause_suggestion,
          capa_recommendation: aiInsights.capa_recommendation,
          duplicate_warning: aiInsights.duplicate_warning,
        });
      }
      dispatch(setSaveState("saved"));
      showToast("Complaint saved successfully.");
    } catch (err) {
      dispatch(setSaveState("error"));
      showToast("Failed to save complaint. Check the backend connection.");
    }
  };

  const handleNewComplaint = () => {
    dispatch(resetForm());
    dispatch(resetSession());
    setTab("new");
  };

  return (
    <div className="app-shell">
      <div className="top-nav">
        <div className="top-nav-brand">
          <div className="brand-mark">AI</div>
          <div>
            <div className="brand-title">AIVOA Complaint Management</div>
            <div className="brand-subtitle">API &amp; FDF Quality Assurance</div>
          </div>
        </div>
        <div className="nav-tabs">
          <button className={`nav-tab ${tab === "new" ? "active" : ""}`} onClick={() => setTab("new")}>
            New Complaint
          </button>
          <button className={`nav-tab ${tab === "list" ? "active" : ""}`} onClick={() => setTab("list")}>
            All Complaints
          </button>
        </div>
      </div>

      <div className="page-body">
        {tab === "new" ? (
          <div className="workflow-grid">
            <ComplaintForm onSave={handleSave} saving={saveState === "saving"} />
            <AIAssistantPanel />
          </div>
        ) : (
          <ComplaintsListPage onOpenNew={handleNewComplaint} />
        )}
      </div>

      {toast && <div className="toast">{toast}</div>}
    </div>
  );
}
