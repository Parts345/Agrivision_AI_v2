import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Notice, ProbabilityBars } from "../components/ui.jsx";
import { useClassLabel, useI18n } from "../i18n/index.jsx";
import { formatDateTime, formatPercent, localeFor } from "../lib/format.js";
import { getLocation, fetchWeather } from "../services/weather.js";
import { fetchStats } from "../services/api.js";

const CLASSES = ["Bacterialblight", "Blast", "Brownspot", "Healthy", "Sheathrot", "Tungro"];

export default function Dashboard() {
  const { t, lang } = useI18n();
  const labelFor = useClassLabel();
  const [stats, setStats] = useState(null);
  const [statsError, setStatsError] = useState(false);
  const [weather, setWeather] = useState({ status: "loading" });

  useEffect(() => {
    let cancelled = false;
    fetchStats()
      .then((data) => !cancelled && setStats(data))
      .catch(() => !cancelled && setStatsError(true));
    return () => { cancelled = true; };
  }, []);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const location = await getLocation();
      try {
        const current = await fetchWeather(location.latitude, location.longitude);
        if (!cancelled) setWeather({ status: "ok", ...current, isDefault: location.isDefault });
      } catch {
        if (!cancelled) setWeather({ status: "error" });
      }
    })();
    return () => { cancelled = true; };
  }, []);

  const byClass = useMemo(() => {
    const counts = stats?.by_class || {};
    return CLASSES.reduce((acc, key) => ({ ...acc, [key]: counts[key] || 0 }), {});
  }, [stats]);

  const probabilitiesForBars = useMemo(() => {
    const total = Object.values(byClass).reduce((a, b) => a + b, 0);
    if (!total) return {};
    return Object.fromEntries(Object.entries(byClass).map(([k, v]) => [k, v / total]));
  }, [byClass]);

  const mostCommon = useMemo(() => {
    const entries = Object.entries(byClass).filter(([, v]) => v > 0).sort((a, b) => b[1] - a[1]);
    return entries.length ? labelFor(entries[0][0]) : t("dashboard.none");
  }, [byClass, labelFor, t]);

  const maxDaily = Math.max(1, ...(stats?.daily || []).map((d) => d.count));
  const dayFormatter = new Intl.DateTimeFormat(localeFor(lang), { day: "numeric", month: "short" });

  return (
    <div className="container">
      <h1>{t("dashboard.title")}</h1>
      <p className="muted">{t("dashboard.intro")}</p>

      {statsError && <Notice kind="error">{t("dashboard.statsError")}</Notice>}

      <section className="section grid grid-3">
        <div className="card stat">
          <p className="label">{t("dashboard.totalScans")}</p>
          <p className="value">{stats ? stats.total_scans : "–"}</p>
        </div>
        <div className="card stat">
          <p className="label">{t("dashboard.last7")}</p>
          <p className="value">{stats ? stats.scans_last_7_days : "–"}</p>
        </div>
        <div className="card stat">
          <p className="label">{t("dashboard.mostCommon")}</p>
          <p className="value" style={{ fontSize: "1.25rem" }}>{stats ? mostCommon : "–"}</p>
        </div>
      </section>

      <section className="section columns">
        <div className="card">
          <h2 className="section-title">{t("dashboard.byDisease")}</h2>
          {stats && stats.total_scans > 0 ? (
            <ProbabilityBars probabilities={probabilitiesForBars} />
          ) : (
            <p className="muted">{t("dashboard.noData")}</p>
          )}
        </div>

        <div className="card">
          <h2 className="section-title">{t("dashboard.weather")}</h2>
          {weather.status === "loading" && <p className="muted">{t("dashboard.locating")}</p>}
          {weather.status === "error" && <p className="muted">{t("dashboard.weatherUnavailable")}</p>}
          {weather.status === "ok" && (
            <>
              <p className="small muted">
                {t("dashboard.weatherFrom")}{" "}
                {weather.isDefault ? t("dashboard.defaultLocation") : t("dashboard.yourLocation")}
              </p>
              <div className="grid grid-3" style={{ marginTop: 8 }}>
                <div><p className="label small muted">{t("dashboard.temperature")}</p><strong>{weather.temperature}°C</strong></div>
                <div><p className="label small muted">{t("dashboard.humidity")}</p><strong>{weather.humidity}%</strong></div>
                <div><p className="label small muted">{t("dashboard.wind")}</p><strong>{weather.wind} km/h</strong></div>
              </div>
            </>
          )}
        </div>
      </section>

      <section className="section card">
        <h2 className="section-title">{t("dashboard.trend")}</h2>
        {stats ? (
          <div className="trend" role="img" aria-label={t("dashboard.trend")}>
            {stats.daily.map((day) => (
              <div className="trend-col" key={day.day} title={`${day.day}: ${day.count}`}>
                <div className="trend-bar" style={{ height: `${(day.count / maxDaily) * 100}%`, opacity: day.count ? 1 : 0.15 }} />
                <span className="trend-label">{dayFormatter.format(new Date(day.day))}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="muted">{t("common.loading")}</p>
        )}
      </section>

      <section className="section card">
        <h2 className="section-title">{t("dashboard.recent")}</h2>
        {stats && stats.recent.length === 0 && <p className="muted">{t("dashboard.noData")}</p>}
        {stats && stats.recent.length > 0 && (
          <ul className="plain">
            {stats.recent.map((scan, index) => (
              <li key={`${scan.created_at}-${index}`}>
                {formatDateTime(scan.created_at, lang)} — <strong>{labelFor(scan.predicted_class)}</strong>{" "}
                <span className="muted">({formatPercent(scan.confidence)})</span>
              </li>
            ))}
          </ul>
        )}
        <p className="small" style={{ marginTop: 16 }}>
          <Link to="/detect">{t("nav.detect")} →</Link>
        </p>
      </section>
    </div>
  );
}
