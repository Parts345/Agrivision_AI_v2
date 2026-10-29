import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { strings, LANGUAGES } from "./strings.js";
import { diseaseText, riskText } from "./diseases.js";

const STORAGE_KEY = "agrivision-lang";
const ENGLISH_LABELS = {
  Bacterialblight: "Bacterial Blight",
  Blast: "Blast",
  Brownspot: "Brown Spot",
  Healthy: "Healthy",
  Sheathrot: "Sheath Rot",
  Tungro: "Tungro"
};
const LanguageContext = createContext(null);

function initialLanguage() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved && strings[saved]) return saved;
  } catch {
    /* storage can be blocked; fall back to browser language */
  }
  const browser = (navigator.language || "en").slice(0, 2);
  return strings[browser] ? browser : "en";
}

export function LanguageProvider({ children }) {
  const [lang, setLang] = useState(initialLanguage);

  useEffect(() => {
    document.documentElement.lang = lang;
    try {
      localStorage.setItem(STORAGE_KEY, lang);
    } catch {
      /* ignore */
    }
  }, [lang]);

  const value = useMemo(() => {
    const dictionary = strings[lang];
    // Dotted lookup, e.g. t("home.title"). Falls back to English, then to the key.
    const t = (key) => {
      const read = (dict) => key.split(".").reduce((node, part) => node?.[part], dict);
      const found = read(dictionary);
      if (found !== undefined) return found;
      const fallback = read(strings.en);
      return fallback !== undefined ? fallback : key;
    };
    return { lang, setLang, t, languages: LANGUAGES };
  }, [lang]);

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export function useI18n() {
  const ctx = useContext(LanguageContext);
  if (!ctx) throw new Error("useI18n must be used inside LanguageProvider");
  return ctx;
}

// Returns localized disease content. English comes straight from the API response.
export function useDiseaseText() {
  const { lang } = useI18n();
  return useCallback(
    (classKey, apiData) => {
      if (lang === "en" || !diseaseText[lang]?.[classKey]) {
        return {
          label: apiData?.predicted_label ?? apiData?.label ?? ENGLISH_LABELS[classKey] ?? classKey,
          description: apiData?.description ?? "",
          symptoms: apiData?.symptoms ?? [],
          causes: apiData?.causes ?? [],
          prevention: apiData?.prevention ?? [],
          treatment: apiData?.treatment ?? [],
          risk: riskText.en[apiData?.risk_level] ?? apiData?.risk_level ?? ""
        };
      }
      const text = diseaseText[lang][classKey];
      return {
        label: text.label,
        description: text.description,
        symptoms: text.symptoms,
        causes: text.causes,
        prevention: text.prevention,
        treatment: text.treatment,
        risk: riskText[lang][apiData?.risk_level] ?? apiData?.risk_level ?? ""
      };
    },
    [lang]
  );
}

export function useClassLabel() {
  const diseaseTextFor = useDiseaseText();
  return useCallback((classKey) => diseaseTextFor(classKey, null).label, [diseaseTextFor]);
}
