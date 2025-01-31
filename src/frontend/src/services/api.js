import axios from 'axios';

const API_URL = "http://172.25.184.18:5050";

export const api = {
  lookupDemographics: async (region) => {
    const response = await axios.post(
      `${API_URL}/lookup_demographics`,
      null,
      {
        params: { region },
        headers: { "Content-Type": "application/json" },
      }
    );
    return response.data;
  },

  discuss: async (params) => {
    const response = await axios.post(
      `${API_URL}/discuss`,
      params,
      {
        headers: { "Content-Type": "application/json" },
      }
    );
    return response.data;
  }
}; 