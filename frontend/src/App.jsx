import { useEffect, useState } from "react";
import { NavLink, Route, Routes } from "react-router-dom";
import { Leaf, Moon, Sun } from "lucide-react";
import Landing from "./pages/Landing.jsx";
import Detect from "./pages/Detect.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import { HistoryDetail, HistoryList } from "./pages/History.jsx";
import NotFound from "./pages/NotFound.jsx";
import { useI18n } from "./i18n/index.jsx";

function useTheme() {
  const [theme, setTheme] = useState(() => {
    try {
      return localStorage.getItem("theme") === "light" ? "light" : "dark";
    } catch {
      return "dark";
    }
  });

  useEffect(() => {
    document.documentElement.classList.toggle("light", theme === "light");
    try {
      localStorage.setItem("theme", theme);
    } catch {
      /* storage blocked: theme still applies for this visit */
    }
  }, [theme]);

  return [theme, setTheme];
}

function Header({ theme, setTheme }) {
  const { t, lang, setLang, languages } = useI18n();
  const links = [
    { to: "/", label: t("nav.home"), end: true },
    { to: "/detect", label: t("nav.detect") },
    { to: "/dashboard", label: t("nav.dashboard") },
    { to: "/history", label: t("nav.history") }
  ];

  return (
    <header className="site-header no-print">
      <div className="inner">
        <NavLink to="/" className="brand" aria-label={t("appName")}>
          <span className="brand-mark" aria-hidden="true"><Leaf size={22} /></span>
          <span>
            <span className="brand-name">{t("appName")}</span>
            <span className="brand-tag">{t("tagline")}</span>
          </span>
        </NavLink>

        <nav className="nav" aria-label="Main">
          {links.map((link) => (
            <NavLink key={link.to} to={link.to} end={link.end} className={({ isActive }) => (isActive ? "active" : "")}>
              {link.label}
            </NavLink>
          ))}
        </nav>

        <div className="header-tools">
          <button
            type="button"
            className="icon-btn"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            aria-label={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
            title={theme === "dark" ? "Light mode" : "Dark mode"}
          >
            {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
          </button>
          <div className="lang-switch" role="group" aria-label={t("language")}>
            {languages.map((item) => (
              <button
                key={item.code}
                type="button"
                aria-pressed={lang === item.code}
                onClick={() => setLang(item.code)}
                lang={item.code}
              >
                {item.name}
              </button>
            ))}
          </div>
        </div>
      </div>
    </header>
  );
}

function Footer() {
  const { t } = useI18n();
  return (
    <footer className="footer no-print">
      <div className="container">{t("footerNote")}</div>
    </footer>
  );
}

export default function App() {
  const [theme, setTheme] = useTheme();
  return (
    <>
      <Header theme={theme} setTheme={setTheme} />
      <main className="page">
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/detect" element={<Detect />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/history" element={<HistoryList />} />
          <Route path="/history/:id" element={<HistoryDetail />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
      <Footer />
    </>
  );
}
