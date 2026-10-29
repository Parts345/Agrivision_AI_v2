import axios from "axios";
import { getDeviceId } from "../lib/device.js";

export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

const api = axios.create({ baseURL: API_BASE_URL, timeout: 120000 });

const deviceHeaders = () => ({ "X-Device-ID": getDeviceId() });

export async function predictDisease(file) {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await api.post("/predict", formData, {
    headers: { ...deviceHeaders(), "Content-Type": "multipart/form-data" }
  });
  return data;
}

export async function fetchStats() {
  const { data } = await api.get("/stats");
  return data;
}

export async function fetchScans({ limit = 10, offset = 0 } = {}) {
  const { data } = await api.get("/scans", { params: { limit, offset }, headers: deviceHeaders() });
  return data;
}

export async function fetchScan(scanId) {
  const { data } = await api.get(`/scans/${scanId}`, { headers: deviceHeaders() });
  return data;
}

export async function deleteScan(scanId) {
  await api.delete(`/scans/${scanId}`, { headers: deviceHeaders() });
}

// Thumbnails need the device header, so they are fetched as blobs and shown via object URLs.
export async function fetchThumbnailUrl(scanId) {
  const response = await api.get(`/scans/${scanId}/thumbnail`, {
    headers: deviceHeaders(),
    responseType: "blob"
  });
  return URL.createObjectURL(response.data);
}

export function isOfflineError(error) {
  return !error?.response;
}

export function errorDetail(error) {
  const detail = error?.response?.data?.detail;
  if (typeof detail === "string" && detail.trim()) return detail;
  if (Array.isArray(detail) && detail.length) return detail.map((item) => item?.msg || "").join(" ");
  return "";
}
