// Anonymous device id used to group scans. It is created once per browser and
// is not linked to any account or personal information.
const KEY = "agrivision-device-id";

export function getDeviceId() {
  try {
    let id = localStorage.getItem(KEY);
    if (!id || !/^[A-Za-z0-9-]{8,64}$/.test(id)) {
      id = crypto.randomUUID ? crypto.randomUUID() : fallbackId();
      localStorage.setItem(KEY, id);
    }
    return id;
  } catch {
    // Storage blocked (private mode): use an id that lasts for this page session only.
    if (!window.__agriDeviceId) window.__agriDeviceId = fallbackId();
    return window.__agriDeviceId;
  }
}

function fallbackId() {
  const part = () => Math.random().toString(36).slice(2, 10);
  return `${part()}-${part()}-${part()}`;
}
