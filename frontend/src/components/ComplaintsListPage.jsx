import React, { useEffect, useState } from "react";
import { listComplaints, deleteComplaint } from "../api/client";

const STATUS_LABEL = {
  pending_triage: "Pending Triage",
  in_review: "In Review",
  closed: "Closed",
};

export default function ComplaintsListPage({ onOpenNew }) {
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);

  const load = () => {
    setLoading(true);
    listComplaints()
      .then(setComplaints)
      .catch(() => setErrorMsg("Could not load complaints. Is the backend running?"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this complaint record?")) return;
    await deleteComplaint(id);
    load();
  };

  return (
    <div className="card">
      <div className="card-header">
        <div>
          <h2 className="card-title">All Complaints</h2>
          <div className="card-subtitle">{complaints.length} record{complaints.length !== 1 ? "s" : ""}</div>
        </div>
        <button className="btn btn-primary" onClick={onOpenNew}>
          + New Complaint
        </button>
      </div>

      {loading ? (
        <div className="empty-state">Loading...</div>
      ) : errorMsg ? (
        <div className="empty-state">{errorMsg}</div>
      ) : complaints.length === 0 ? (
        <div className="empty-state">No complaints logged yet. Click "New Complaint" to get started.</div>
      ) : (
        <div style={{ overflowX: "auto" }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Product</th>
                <th>Batch</th>
                <th>Customer</th>
                <th>Type</th>
                <th>Severity</th>
                <th>Risk (AI)</th>
                <th>Status</th>
                <th>Logged</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {complaints.map((c) => (
                <tr key={c.id}>
                  <td>{c.product_name || "—"}</td>
                  <td>{c.batch_number || "—"}</td>
                  <td>{c.customer_name || "—"}</td>
                  <td>{c.complaint_type || "—"}</td>
                  <td>{c.initial_severity || "—"}</td>
                  <td>
                    {c.risk_classification ? (
                      <span className={`risk-pill ${c.risk_classification}`}>{c.risk_classification}</span>
                    ) : (
                      "—"
                    )}
                  </td>
                  <td>
                    <span className={`status-chip ${c.status}`}>{STATUS_LABEL[c.status] || c.status}</span>
                  </td>
                  <td>{new Date(c.created_at).toLocaleDateString()}</td>
                  <td>
                    <button className="btn btn-ghost" onClick={() => handleDelete(c.id)}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
