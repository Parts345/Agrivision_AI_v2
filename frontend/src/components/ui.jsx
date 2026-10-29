import { useId } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  LabelList,
  ResponsiveContainer,
  XAxis,
  YAxis
} from "recharts";
import { useClassLabel, useDiseaseText, useI18n } from "../i18n/index.jsx";
import { formatPercent } from "../lib/format.js";

export function Notice({ kind = "", className = "", children }) {
  return <div className={`notice ${kind} ${className}`.trim()} role={kind === "error" ? "alert" : "status"}>{children}</div>;
}

export function ProbabilityBars({ probabilities }) {
  const labelFor = useClassLabel();
  const rows = Object.entries(probabilities || {}).sort((a, b) => b[1] - a[1]);
  return (
    <div>
      {rows.map(([classKey, value]) => (
        <div className="bar-row" key={classKey}>
          <span>{labelFor(classKey)}</span>
          <div className="bar-track" aria-hidden="true">
            <div className="bar-fill" style={{ width: `${Math.max(0.5, value * 100)}%` }} />
          </div>
          <span className="bar-value">{formatPercent(value)}</span>
        </div>
      ))}
    </div>
  );
}

function riskClass(level) {
  if (level === "High") return "high";
  if (level === "Medium") return "medium";
  return "";
}

function ProbabilityChart({ probabilities }) {
  const labelFor = useClassLabel();
  const gradientId = `probability-gradient-${useId().replace(/:/g, "")}`;
  const data = Object.entries(probabilities || {}).map(([classKey, value]) => ({
    name: labelFor(classKey),
    value
  }));

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} margin={{ top: 24, right: 8, bottom: 4, left: 0 }}>
        <defs>
          <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="var(--accent)" />
            <stop offset="100%" stopColor="var(--accent-2)" />
          </linearGradient>
        </defs>
        <CartesianGrid vertical={false} stroke="var(--line)" strokeDasharray="3 3" />
        <XAxis
          dataKey="name"
          interval={0}
          angle={-30}
          textAnchor="end"
          height={54}
          tick={{ fill: "var(--muted)", fontSize: 11 }}
          axisLine={{ stroke: "var(--line)" }}
          tickLine={false}
        />
        <YAxis
          domain={[0, 1]}
          tickFormatter={formatPercent}
          width={42}
          tick={{ fill: "var(--muted)", fontSize: 11 }}
          axisLine={false}
          tickLine={false}
        />
        <Bar dataKey="value" fill={`url(#${gradientId})`} radius={[6, 6, 0, 0]} maxBarSize={42}>
          <LabelList dataKey="value" position="top" formatter={formatPercent} fill="var(--text)" />
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

// Full disease result. Used on the Detect page and in history details.
export function DiseaseResult({ data, showLowConfidence = false }) {
  const { t } = useI18n();
  const text = useDiseaseText()(data.predicted_class, data);

  return (
    <div className="stack disease-result">
      <section className="card stack result-card">
        <div className="result-head">
          <div>
            <p className="muted small" style={{ margin: 0 }}>{t("detect.resultTitle")}</p>
            <h2 className="result-name">{text.label}</h2>
            <p style={{ marginTop: 8 }}>{text.description}</p>
            <span className={`risk-tag ${riskClass(data.risk_level)}`}>
              {t("detect.riskLabel")}: {text.risk}
            </span>
          </div>
        </div>

        <div className="result-metrics">
          <div className="confidence-group">
            <span className="small muted">{t("detect.confidence")}</span>
            <div className="confidence">
              <strong>{formatPercent(data.confidence)}</strong>
            </div>
          </div>
          <section className="probability-panel">
            <h3>{t("detect.probabilitiesTitle")}</h3>
            <ProbabilityChart probabilities={data.probabilities} />
            <p className="class-name">
              Actual Class Name: <code>{data.predicted_class}</code>
            </p>
          </section>
        </div>
      </section>

      {showLowConfidence && data.confidence < 0.6 && (
        <Notice kind="warn">{t("detect.lowConfidence")}</Notice>
      )}

      <div className="columns result-lists">
        <section className="card">
          <h3>{t("detect.symptoms")}</h3>
          <ul className="plain"><ListItems items={text.symptoms} /></ul>
        </section>
        <section className="card">
          <h3>{t("detect.causes")}</h3>
          <ul className="plain"><ListItems items={text.causes} /></ul>
        </section>
        <section className="card">
          <h3>{t("detect.prevention")}</h3>
          <ul className="plain"><ListItems items={text.prevention} /></ul>
        </section>
        <section className="card">
          <h3>{t("detect.treatment")}</h3>
          <ul className="plain"><ListItems items={text.treatment} /></ul>
        </section>
      </div>
    </div>
  );
}

function ListItems({ items }) {
  return items.map((item) => <li key={item}>{item}</li>);
}
