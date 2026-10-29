import { Link } from "react-router-dom";
import { useI18n } from "../i18n/index.jsx";

export default function NotFound() {
  const { t } = useI18n();
  return (
    <div className="container">
      <h1>{t("common.notFoundTitle")}</h1>
      <p className="muted">{t("common.notFoundText")}</p>
      <Link to="/" className="btn">{t("common.goHome")}</Link>
    </div>
  );
}
