import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { setField, resetForm } from "../store/complaintSlice";

const SOURCE_OPTIONS = ["Email", "Phone Call", "Web Portal", "Regulatory Authority", "Field Sales Rep", "Letter", "Other"];
const TYPE_OPTIONS = [
  "Product Quality Defect",
  "Packaging Defect",
  "Labeling Error",
  "Adverse Event",
  "Foreign Particulate",
  "Delivery/Shipping Issue",
  "Documentation Discrepancy",
  "Other",
];
const SEVERITY_OPTIONS = ["Critical", "Major", "Minor"];
const PRIORITY_OPTIONS = ["High", "Medium", "Low"];

function Field({ label, name, fields, onChange, type = "text", options, textarea, unit }) {
  const value = fields[name] || "";
  const filled = Boolean(value);
  const placeholder = "Awaiting AI extraction...";

  return (
    <div className="form-field">
      <label htmlFor={name}>{label}</label>
      {options ? (
        <select id={name} className={filled ? "ai-filled" : ""} value={value} onChange={(e) => onChange(name, e.target.value)}>
          <option value="">{placeholder}</option>
          {options.map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
      ) : textarea ? (
        <textarea
          id={name}
          className={filled ? "ai-filled" : ""}
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange(name, e.target.value)}
        />
      ) : (
        <input
          id={name}
          type={type}
          className={filled ? "ai-filled" : ""}
          placeholder={unit ? `${placeholder} (${unit})` : placeholder}
          value={value}
          onChange={(e) => onChange(name, e.target.value)}
        />
      )}
    </div>
  );
}

const STATUS_LABEL = {
  pending_triage: "Pending Triage",
  in_review: "In Review",
  closed: "Closed",
};

export default function ComplaintForm({ onSave, saving }) {
  const dispatch = useDispatch();
  const fields = useSelector((s) => s.complaint.fields);
  const status = useSelector((s) => s.complaint.status);

  const onChange = (name, value) => dispatch(setField({ name, value }));

  return (
    <div className="card">
      <div className="card-header">
        <div>
          <h2 className="card-title">Log Customer Complaint</h2>
          <div className="card-subtitle">API &amp; FDF Quality Assurance Module</div>
        </div>
        <span className={`status-chip ${status}`}>{STATUS_LABEL[status] || status}</span>
      </div>

      <div className="form-body">
        <div className="form-section">
          <div className="form-section-title">1. Origin &amp; Customer Details</div>
          <div className="form-row">
            <Field label="Complaint Source" name="complaint_source" fields={fields} onChange={onChange} options={SOURCE_OPTIONS} />
            <Field label="Customer Name" name="customer_name" fields={fields} onChange={onChange} />
          </div>
        </div>

        <div className="form-section">
          <div className="form-section-title">2. Product &amp; Batch Identification</div>
          <div className="form-row">
            <Field label="Product Name" name="product_name" fields={fields} onChange={onChange} />
            <Field label="Product Strength/Grade" name="product_strength" fields={fields} onChange={onChange} />
          </div>
          <div className="form-row">
            <Field label="Batch/Lot Number" name="batch_number" fields={fields} onChange={onChange} />
            <Field label="Manufacturing Date" name="manufacturing_date" fields={fields} onChange={onChange} type="date" />
          </div>
          <div className="form-row">
            <Field label="Expiry Date" name="expiry_date" fields={fields} onChange={onChange} type="date" />
            <Field label="Quantity Affected" name="quantity_affected" fields={fields} onChange={onChange} unit="e.g. units, kg" />
          </div>
        </div>

        <div className="form-section">
          <div className="form-section-title">3. Complaint Details</div>
          <div className="form-row">
            <Field label="Complaint Type" name="complaint_type" fields={fields} onChange={onChange} options={TYPE_OPTIONS} />
            <Field label="Complaint Date" name="complaint_date" fields={fields} onChange={onChange} type="date" />
          </div>
          <div className="form-row" style={{ gridTemplateColumns: "1fr" }}>
            <Field label="Detailed Complaint Description" name="complaint_description" fields={fields} onChange={onChange} textarea />
          </div>
        </div>

        <div className="form-section">
          <div className="form-section-title">4. Initial Assessment &amp; Priority</div>
          <div className="form-row">
            <Field label="Initial Severity" name="initial_severity" fields={fields} onChange={onChange} options={SEVERITY_OPTIONS} />
            <Field label="Priority" name="priority" fields={fields} onChange={onChange} options={PRIORITY_OPTIONS} />
          </div>
        </div>
      </div>

      <div className="form-actions">
        <button className="btn btn-ghost" onClick={() => dispatch(resetForm())} disabled={saving}>
          ↺ Reset Form
        </button>
        <button className="btn btn-primary" onClick={onSave} disabled={saving}>
          🖫 {saving ? "Saving..." : "Save Complaint"}
        </button>
      </div>
    </div>
  );
}
