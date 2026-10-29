import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { DiseaseResult, Notice } from "../components/ui.jsx";
import { useClassLabel, useI18n } from "../i18n/index.jsx";
import { formatDateTime, formatPercent } from "../lib/format.js";
import { deleteScan, errorDetail, fetchScan, fetchScans, fetchThumbnailUrl, isOfflineError } from "../services/api.js";

const PAGE_SIZE = 10;

function loadError(err, t) {
  return isOfflineError(err) ? t("detect.offline") : errorDetail(err) || t("history.loadError");
}

// Loads a thumbnail with the device header and frees the object URL on unmount.
function Thumbnail({ scanId }) {
  const [src, setSrc] = useState("");
  useEffect(() => {
    let url = "";
    let cancelled = false;
    fetchThumbnailUrl(scanId)
      .then((created) => {
        url = created;
        if (cancelled) URL.revokeObjectURL(created);
        else setSrc(created);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
      if (url) URL.revokeObjectURL(url);
    };
  }, [scanId]);
  return src ? <img className="scan-thumb" src={src} alt="" /> : <div className="scan-thumb" aria-hidden="true" />;
}

export function HistoryList() {
  const { t, lang } = useI18n();
  const labelFor = useClassLabel();
  const navigate = useNavigate();
  const [page, setPage] = useState(0);
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const load = useCallback(async () => {
    setError("");
    try {
      setData(await fetchScans({ limit: PAGE_SIZE, offset: page * PAGE_SIZE }));
    } catch (err) {
      setError(loadError(err, t));
    }
  }, [page, t]);

  useEffect(() => { load(); }, [load]);

  const remove = async (id) => {
    if (!window.confirm(t("history.confirmDelete"))) return;
    try {
      await deleteScan(id);
      setMessage(t("history.deleted"));
      load();
    } catch (err) {
      setError(loadError(err, t));
    }
  };

  const totalPages = data ? Math.max(1, Math.ceil(data.total / PAGE_SIZE)) : 1;

  return (
    <div className="container">
      <h1>{t("history.title")}</h1>
      <p className="muted">{t("history.intro")}</p>

      {error && <Notice kind="error">{error}</Notice>}
      {message && <Notice kind="ok">{message}</Notice>}

      {!data && !error && <p className="muted">{t("common.loading")}</p>}

      {data && data.total === 0 && (
        <div className="card" style={{ marginTop: 16 }}>
          <p>{t("history.empty")}</p>
          <Link to="/detect" className="btn">{t("history.startScan")}</Link>
        </div>
      )}

      {data && data.items.length > 0 && (
        <>
          <ul className="scan-list" style={{ marginTop: 16 }}>
            {data.items.map((scan) => (
              <li className="card scan-item" key={scan.id}>
                {scan.has_thumbnail ? <Thumbnail scanId={scan.id} /> : <div className="scan-thumb" />}
                <div>
                  <strong>{labelFor(scan.predicted_class)}</strong>
                  <div className="small muted">{formatDateTime(scan.created_at, lang)} · {formatPercent(scan.confidence)}</div>
                </div>
                <div className="scan-actions" style={{ display: "flex", gap: 8 }}>
                  <button type="button" className="btn small-btn secondary" onClick={() => navigate(`/history/${scan.id}`)}>
                    {t("history.open")}
                  </button>
                  <button type="button" className="btn small-btn danger" onClick={() => remove(scan.id)}>
                    {t("history.delete")}
                  </button>
                </div>
              </li>
            ))}
          </ul>

          {totalPages > 1 && (
            <div className="pager">
              <button type="button" className="btn small-btn secondary" onClick={() => setPage((p) => p - 1)} disabled={page === 0}>
                {t("history.previous")}
              </button>
              <span className="small muted">{page + 1} / {totalPages}</span>
              <button type="button" className="btn small-btn secondary" onClick={() => setPage((p) => p + 1)} disabled={page + 1 >= totalPages}>
                {t("history.next")}
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export function HistoryDetail() {
  const { t, lang } = useI18n();
  const { id } = useParams();
  const navigate = useNavigate();
  const [scan, setScan] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    setScan(null);
    setError("");
    fetchScan(id)
      .then((data) => !cancelled && setScan(data))
      .catch((err) => !cancelled && setError(loadError(err, t)));
    return () => { cancelled = true; };
  }, [id, t]);

  const remove = async () => {
    if (!window.confirm(t("history.confirmDelete"))) return;
    try {
      await deleteScan(id);
      navigate("/history");
    } catch (err) {
      setError(loadError(err, t));
    }
  };

  return (
    <div className="container">
      <p><Link to="/history">← {t("history.back")}</Link></p>
      {error && <Notice kind="error">{error}</Notice>}
      {!scan && !error && <p className="muted">{t("common.loading")}</p>}
      {scan && (
        <div className="stack">
          <p className="small muted" style={{ margin: 0 }}>{t("history.date")}: {formatDateTime(scan.created_at, lang)}</p>
          <DiseaseResult data={scan} />
          <div className="button-row no-print">
            <button type="button" className="btn secondary" onClick={() => window.print()}>{t("detect.print")}</button>
            <button type="button" className="btn danger" onClick={remove}>{t("history.delete")}</button>
          </div>
        </div>
      )}
    </div>
  );
}
