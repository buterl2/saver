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

/**
 * Fetch deliveries past data
 */
export const fetchDeliveriesPast = async () => {
  return apiFetch(API_ENDPOINTS.DELIVERIES_PAST);
};

/**
 * Fetch deliveries today data
 */
export const fetchDeliveriesToday = async () => {
  return apiFetch(API_ENDPOINTS.DELIVERIES_TODAY);
};

/**
 * Fetch deliveries future data
 */
export const fetchDeliveriesFuture = async () => {
  return apiFetch(API_ENDPOINTS.DELIVERIES_FUTURE);
};

/**
 * Fetch HU past data
 */
export const fetchHuPast = async () => {
  return apiFetch(API_ENDPOINTS.HU_PAST);
};

/**
 * Fetch HU today data
 */
export const fetchHuToday = async () => {
  return apiFetch(API_ENDPOINTS.HU_TODAY);
};

/**
 * Fetch HU future data
 */
export const fetchHuFuture = async () => {
  return apiFetch(API_ENDPOINTS.HU_FUTURE);
};

/**
 * Fetch deliveries dashboard data
 */
export const fetchDeliveriesDashboard = async () => {
  return apiFetch(API_ENDPOINTS.DELIVERIES_DASHBOARD);
};

/**
 * Fetch HU dashboard data
 */
export const fetchHuDashboard = async () => {
  return apiFetch(API_ENDPOINTS.HU_DASHBOARD);
};

/**
 * Fetch lines dashboard data
 */
export const fetchLinesDashboard = async () => {
  return apiFetch(API_ENDPOINTS.LINES_DASHBOARD);
};

/**
 * Fetch deliveries PGI dashboard data
 */
export const fetchDeliveriesPgiDashboard = async () => {
  return apiFetch(API_ENDPOINTS.DELIVERIES_PGI_DASHBOARD);
};

/**
 * Fetch HU PGI dashboard data
 */
export const fetchHuPgiDashboard = async () => {
  return apiFetch(API_ENDPOINTS.HU_PGI_DASHBOARD);
};

/**
 * Fetch lines PGI dashboard data
 */
export const fetchLinesPgiDashboard = async () => {
  return apiFetch(API_ENDPOINTS.LINES_PGI_DASHBOARD);
};

/**
 * Fetch lines hourly dashboard data
 */
export const fetchLinesHourlyDashboard = async () => {
  return apiFetch(API_ENDPOINTS.LINES_HOURLY_DASHBOARD);
};

