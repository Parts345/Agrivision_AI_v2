import { Link } from "react-router-dom";
import { useClassLabel, useI18n } from "../i18n/index.jsx";

const CLASSES = ["Bacterialblight", "Blast", "Brownspot", "Healthy", "Sheathrot", "Tungro"];

export default function Landing() {
  const { t } = useI18n();
  const labelFor = useClassLabel();

  return (
    <div className="container">
      <section className="hero">
        <div>
          <h1>{t("home.title")}</h1>
          <p className="lead">{t("home.intro")}</p>
          <div className="actions">
            <Link to="/detect" className="btn">{t("home.primary")}</Link>
            <Link to="/dashboard" className="btn secondary">{t("home.secondary")}</Link>
          </div>
        </div>
      </section>

      <section className="section">
        <h2 className="section-title">{t("home.detectsTitle")}</h2>
        <p className="muted">{t("home.detectsIntro")}</p>
        <div className="grid grid-3">
          {CLASSES.map((key) => (
            <div className="card detect-card" key={key}>
              <h3 style={{ fontSize: "1.05rem" }}>{labelFor(key)}</h3>
            </div>
          ))}
        </div>
      </section>

      <section className="section columns">
        <div className="card">
          <h2 className="section-title">{t("home.tipsTitle")}</h2>
          <ul className="plain">
            {t("home.tips").map((tip) => <li key={tip}>{tip}</li>)}
          </ul>
        </div>
        <div className="card">
          <h2 className="section-title">{t("home.limitsTitle")}</h2>
          <ul className="plain">
            {t("home.limits").map((item) => <li key={item}>{item}</li>)}
          </ul>
        </div>
      </section>
    </div>
  );
}
