import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { DiseaseResult, Notice } from "../components/ui.jsx";
import { useI18n } from "../i18n/index.jsx";
import { prepareImage } from "../lib/imageCompress.js";
import { errorDetail, isOfflineError, predictDisease } from "../services/api.js";

const MAX_ORIGINAL_MB = 30;

export default function Detect() {
  const { t } = useI18n();
  const galleryRef = useRef(null);
  const cameraRef = useRef(null);

  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const requestRef = useRef(0);

  // Free the preview URL when it changes or the page closes.
  useEffect(() => () => preview && URL.revokeObjectURL(preview), [preview]);

  const chooseFile = (selected) => {
    if (!selected) return;
    setError("");
    if (!selected.type.startsWith("image/")) return setError(t("detect.notImage"));
    if (selected.size > MAX_ORIGINAL_MB * 1024 * 1024) return setError(t("detect.tooLarge"));
    requestRef.current += 1;
    setFile(selected);
    setPreview(URL.createObjectURL(selected));
    setResult(null);
    setLoading(false);
  };

  const onInputChange = (event) => {
    chooseFile(event.target.files?.[0]);
    event.target.value = ""; // allow picking the same file again
  };

  const clear = () => {
    requestRef.current += 1;
    setFile(null);
    setPreview("");
    setResult(null);
    setError("");
    setLoading(false);
  };

  const analyze = async () => {
    if (!file) return setError(t("detect.noFile"));
    const id = requestRef.current;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const prepared = await prepareImage(file);
      const data = await predictDisease(prepared);
      if (id !== requestRef.current) return;
      setResult(data);
    } catch (err) {
      if (id !== requestRef.current) return;
      if (isOfflineError(err)) setError(t("detect.offline"));
      else setError(errorDetail(err) || t("detect.failed"));
    } finally {
      if (id === requestRef.current) setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>{t("detect.title")}</h1>
      <p className="muted">{t("detect.intro")}</p>

      <div className="columns" style={{ marginTop: 20 }}>
        <section className="card">
          <div className="upload-box">
            {preview ? (
              <img src={preview} alt="" />
            ) : (
              <div>
                <h2 style={{ fontSize: "1.2rem" }}>{t("detect.emptyTitle")}</h2>
                <p className="muted small">{t("detect.emptyText")}</p>
              </div>
            )}
          </div>

          <input ref={galleryRef} type="file" accept="image/*" hidden onChange={onInputChange} />
          <input ref={cameraRef} type="file" accept="image/*" capture="environment" hidden onChange={onInputChange} />

          <div className="button-row">
            <button type="button" className="btn secondary" onClick={() => cameraRef.current?.click()}>
              {t("detect.takePhoto")}
            </button>
            <button type="button" className="btn secondary" onClick={() => galleryRef.current?.click()}>
              {t("detect.choosePhoto")}
            </button>
          </div>

          <div className="button-row">
            <button type="button" className="btn" onClick={analyze} disabled={!file || loading}>
              {loading ? t("detect.analyzing") : t("detect.analyze")}
            </button>
            {file && (
              <button type="button" className="btn danger" onClick={clear} disabled={loading}>
                {t("detect.clear")}
              </button>
            )}
          </div>

          {error && <Notice kind="error">{error}</Notice>}
        </section>

        <section aria-live="polite">
          {!result && !loading && <p className="muted">{t("detect.emptyText")}</p>}
          {loading && <p>{t("detect.analyzing")}</p>}
          {result && (
            <>
              <DiseaseResult data={result} showLowConfidence />
              <div className="stack" style={{ marginTop: 16 }}>
                <Notice kind={result.scan_id ? "ok" : ""} className="notice-line">
                  <span className="notice-line-text">
                    {result.scan_id ? t("detect.savedNote") : t("detect.notSavedNote")}
                  </span>
                  <Link to="/history">{t("detect.view")}</Link>
                </Notice>
              </div>
              <div className="button-row no-print">
                <button type="button" className="btn secondary" onClick={() => window.print()}>
                  {t("detect.print")}
                </button>
                <button type="button" className="btn" onClick={clear}>
                  {t("detect.newScan")}
                </button>
              </div>
            </>
          )}
        </section>
      </div>
    </div>
  );
}
