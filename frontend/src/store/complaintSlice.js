import { createSlice } from "@reduxjs/toolkit";

const emptyFields = {
  complaint_source: "",
  customer_name: "",
  product_name: "",
  product_strength: "",
  batch_number: "",
  manufacturing_date: "",
  expiry_date: "",
  quantity_affected: "",
  complaint_type: "",
  complaint_date: "",
  complaint_description: "",
  initial_severity: "",
  priority: "",
};

const initialState = {
  savedId: null,
  status: "pending_triage", // pending_triage | in_review | closed
  fields: { ...emptyFields },
  aiInsights: {
    completeness_score: null,
    missing_fields: [],
    risk_classification: null,
    risk_rationale: null,
    ai_summary: null,
    root_cause_suggestion: null,
    capa_recommendation: null,
    duplicate_warning: null,
  },
  sourceDocumentName: null,
  saveState: "idle", // idle | saving | saved | error
};

const complaintSlice = createSlice({
  name: "complaint",
  initialState,
  reducers: {
    setField(state, action) {
      const { name, value } = action.payload;
      state.fields[name] = value;
    },
    setFields(state, action) {
      state.fields = { ...state.fields, ...action.payload };
    },
    setAiInsights(state, action) {
      state.aiInsights = { ...state.aiInsights, ...action.payload };
    },
    setSourceDocumentName(state, action) {
      state.sourceDocumentName = action.payload;
    },
    setSavedId(state, action) {
      state.savedId = action.payload;
    },
    setSaveState(state, action) {
      state.saveState = action.payload;
    },
    resetForm() {
      return { ...initialState, fields: { ...emptyFields } };
    },
  },
});

export const {
  setField,
  setFields,
  setAiInsights,
  setSourceDocumentName,
  setSavedId,
  setSaveState,
  resetForm,
} = complaintSlice.actions;

export default complaintSlice.reducer;
