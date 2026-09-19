import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  product_name: '', batch_number: '', originating_site: '', impacted_npm: '',
  complaint_category: '', product_defect: '', complaint_description: '',
  severity: '', suggested_next_action: '', initial_risk_assessment: ''
};

const complaintSlice = createSlice({
  name: 'complaint',
  initialState,
  reducers: {
    mergeComplaintData: (state, action) => {
      const aiData = action.payload;

      const isNewProduct = aiData.product_name !== "" && state.product_name !== "" && aiData.product_name !== state.product_name;
      const isNewDefect = aiData.product_defect !== "" && state.product_defect !== "" && aiData.product_defect !== state.product_defect;

      if (isNewProduct && isNewDefect) {
        Object.keys(initialState).forEach(key => {
          state[key] = initialState[key];
        });
      }

      for (const key in aiData) {
        if (aiData[key] !== "" && aiData[key] !== undefined) {
          state[key] = aiData[key];
        }
      }
    },
    updateField: (state, action) => {
      state[action.payload.name] = action.payload.value;
    },
    resetComplaint: () => initialState
  }
});

export const { mergeComplaintData, updateField, resetComplaint } = complaintSlice.actions;
export default complaintSlice.reducer;