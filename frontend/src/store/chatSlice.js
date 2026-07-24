import { createSlice } from "@reduxjs/toolkit";
import { v4 as uuidv4 } from "./uuid";

const initialState = {
  sessionId: uuidv4(),
  messages: [
    {
      id: "welcome",
      role: "assistant",
      content:
        "Upload a complaint document or paste text above. I will automatically extract the details and populate the form for you.",
    },
  ],
  progressPercent: 0,
  progressLabel: "",
  isExtracting: false,
  isChatting: false,
};

const chatSlice = createSlice({
  name: "chat",
  initialState,
  reducers: {
    addMessage(state, action) {
      state.messages.push({ id: uuidv4(), ...action.payload });
    },
    setProgress(state, action) {
      const { percent, label } = action.payload;
      if (percent !== undefined) state.progressPercent = percent;
      if (label !== undefined) state.progressLabel = label;
    },
    setExtracting(state, action) {
      state.isExtracting = action.payload;
      if (action.payload) {
        state.progressPercent = 10;
        state.progressLabel = "Analyzing document content and extracting key details...";
      }
    },
    setChatting(state, action) {
      state.isChatting = action.payload;
    },
    resetSession(state) {
      state.sessionId = uuidv4();
      state.messages = [initialState.messages[0]];
      state.progressPercent = 0;
      state.progressLabel = "";
    },
  },
});

export const { addMessage, setProgress, setExtracting, setChatting, resetSession } = chatSlice.actions;
export default chatSlice.reducer;
