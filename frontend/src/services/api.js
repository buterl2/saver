import { API_BASE_URL, API_ENDPOINTS } from './config';

/**
 * Generic API fetch function
 */
const apiFetch = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  const response = await fetch(url, config);
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `API Error: ${response.statusText}`);
  }

  return response.json();
};

/**
 * Fetch picking data
 */
export const fetchPickingData = async () => {
  return apiFetch(API_ENDPOINTS.PICKING_DATA);
};

/**
 * Fetch packing data
 */
export const fetchPackingData = async () => {
  return apiFetch(API_ENDPOINTS.PACKING_DATA);
};

/**
 * Fetch users names
 */
export const fetchUsersNames = async () => {
  return apiFetch(API_ENDPOINTS.USERS_NAMES);
};

/**
 * Save users names
 */
export const saveUsersNames = async (data) => {
  return apiFetch(API_ENDPOINTS.USERS_NAMES, {
    method: 'POST',
    body: JSON.stringify(data),
    headers: {
      'Content-Type': 'application/json',
    },
  });
};

/**
 * Print barcode
 */
export const printBarcode = async (data) => {
  return apiFetch(API_ENDPOINTS.BARCODE, {
    method: 'POST',
    body: JSON.stringify(data),
    headers: {
      'Content-Type': 'application/json',
    },
  });
};

