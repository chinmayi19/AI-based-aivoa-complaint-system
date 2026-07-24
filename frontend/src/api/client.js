import axios from "axios";

const api = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || "/api",
});

export const listComplaints = (status) =>
  api.get("/complaints", { params: status ? { status } : {} }).then((r) => r.data);

export const getComplaint = (id) => api.get(`/complaints/${id}`).then((r) => r.data);

export const createComplaint = (payload) => api.post("/complaints", payload).then((r) => r.data);

export const updateComplaint = (id, payload) => api.put(`/complaints/${id}`, payload).then((r) => r.data);

export const deleteComplaint = (id) => api.delete(`/complaints/${id}`);

export const extractFromFile = (file, sessionId) => {
  const form = new FormData();
  form.append("file", file);
  if (sessionId) form.append("session_id", sessionId);
  return api.post("/ai/extract", form, { headers: { "Content-Type": "multipart/form-data" } }).then((r) => r.data);
};

export const extractFromText = (text, sessionId) => {
  const form = new FormData();
  form.append("text", text);
  if (sessionId) form.append("session_id", sessionId);
  return api.post("/ai/extract", form).then((r) => r.data);
};

export const sendChatMessage = (sessionId, message, currentFields) =>
  api
    .post("/ai/chat", { session_id: sessionId, message, current_fields: currentFields })
    .then((r) => r.data);

export const attachAiResults = (complaintId, extractionResponse) =>
  api.post(`/ai/save-with-ai/${complaintId}`, extractionResponse).then((r) => r.data);

export default api;
