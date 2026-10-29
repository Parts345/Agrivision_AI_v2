const LOCALES = { en: "en-IN", mr: "mr-IN", hi: "hi-IN" };

export function formatDateTime(iso, lang) {
  if (!iso) return "";
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "";
  return date.toLocaleString(LOCALES[lang] || "en-IN", { dateStyle: "medium", timeStyle: "short" });
}

export function formatPercent(value) {
  return `${Math.round((value || 0) * 100)}%`;
}

export function localeFor(lang) {
  return LOCALES[lang] || "en-IN";
}
