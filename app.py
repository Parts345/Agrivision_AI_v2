from __future__ import annotations

from datetime import datetime
from io import StringIO
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image

from utils.disease_info import get_disease_details
from utils.prediction import CLASS_NAMES, MODEL_PATH, predict_disease


APP_TITLE = "Rice Disease Detection System"
ROOT_DIR = Path(__file__).resolve().parent
STYLE_PATH = ROOT_DIR / "assets" / "style.css"


def load_css(css_path: Path) -> None:
    """Inject local CSS for a polished Streamlit interface."""
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def configure_page() -> None:
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="R",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    load_css(STYLE_PATH)


def render_sidebar() -> str:
    with st.sidebar:
        st.markdown("<div class='sidebar-brand'>RiceAI</div>", unsafe_allow_html=True)
        st.markdown("AI-assisted rice leaf disease screening for quick field decisions.")

        st.divider()
        page = st.radio(
            "Navigation",
            ["Detection Dashboard", "Disease Intelligence", "Prediction History"],
            label_visibility="visible",
        )

        st.divider()
        st.markdown("### Model Status")
        if MODEL_PATH.exists():
            st.success("Model file found")
        else:
            st.error("Missing model/model.h5")
        st.caption(f"Supported classes: {len(CLASS_NAMES)}")

        st.divider()
        st.info("For best results, upload a clear, close-up image of a single rice leaf under natural light.")
        return page


def render_hero() -> None:
    st.markdown(
        """
        <section class="hero">
            <div>
                <p class="eyebrow">Production AI Dashboard</p>
                <h1>Rice Disease Detection System</h1>
                <p class="hero-copy">
                    Upload a rice leaf image and receive disease prediction, confidence,
                    symptom intelligence, prevention guidance, and treatment recommendations.
                </p>
            </div>
            <div class="hero-stat">
                <span>6</span>
                <small>Disease Classes</small>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, helper: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <span>{label}</span>
            <strong>{value}</strong>
            <small>{helper}</small>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_probability_chart(probability_df: pd.DataFrame) -> None:
    fig = px.bar(
        probability_df.sort_values("Confidence", ascending=True),
        x="Confidence",
        y="Disease",
        orientation="h",
        text=probability_df.sort_values("Confidence", ascending=True)["Confidence"].map(lambda value: f"{value:.1%}"),
        color="Confidence",
        color_continuous_scale=["#2c3e35", "#78c850", "#d7ff8f"],
        range_x=[0, 1],
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#ecfdf5",
        height=390,
        margin=dict(l=10, r=10, t=20, b=10),
        coloraxis_showscale=False,
        xaxis_tickformat=".0%",
        xaxis_title="Model Confidence",
        yaxis_title="",
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    st.plotly_chart(fig, use_container_width=True)


def render_solution_cards(details: dict[str, object]) -> None:
    columns = st.columns(2)
    sections = [
        ("Symptoms", details["symptoms"]),
        ("Causes", details["causes"]),
        ("Prevention", details["prevention"]),
        ("Suggested Treatment", details["treatment"]),
    ]

    for index, (title, items) in enumerate(sections):
        with columns[index % 2]:
            bullet_items = "".join(f"<li>{item}</li>" for item in items)
            st.markdown(
                f"""
                <div class="solution-card">
                    <h3>{title}</h3>
                    <ul>{bullet_items}</ul>
                </div>
                """,
                unsafe_allow_html=True,
            )


def build_report(prediction: str, confidence: float, probability_df: pd.DataFrame, details: dict[str, object]) -> str:
    report = StringIO()
    report.write(f"{APP_TITLE} - Prediction Report\n")
    report.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    report.write(f"Prediction: {prediction}\n")
    report.write(f"Confidence: {confidence:.2%}\n\n")
    report.write("Disease Description\n")
    report.write(f"{details['description']}\n\n")
    for section in ["symptoms", "causes", "prevention", "treatment"]:
        report.write(f"{section.title()}\n")
        for item in details[section]:
            report.write(f"- {item}\n")
        report.write("\n")
    report.write("All Class Probabilities\n")
    report.write(probability_df.to_csv(index=False))
    return report.getvalue()


def render_detection_dashboard() -> None:
    upload_card, guidance_card = st.columns([1.1, 0.9], gap="large")

    with upload_card:
        st.markdown("<div class='section-title'>Upload Rice Leaf Image</div>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Choose a leaf image",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed",
        )

        if uploaded_file is None:
            st.markdown(
                """
                <div class="empty-state">
                    <strong>Waiting for image</strong>
                    <span>Upload a clear leaf photo to start the AI diagnosis.</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            return

        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded rice leaf image", use_container_width=True)

    with guidance_card:
        st.markdown("<div class='section-title'>Field Guidance</div>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class="glass-card">
                <h3>Capture Tips</h3>
                <p>Use a focused image with the affected portion visible. Avoid heavy shadows, mixed leaves, and distant photos.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="glass-card subtle">
                <h3>Decision Support</h3>
                <p>This tool supports early screening. For severe outbreaks, validate with a local agriculture expert.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    try:
        with st.spinner("Analyzing rice leaf image..."):
            result = predict_disease(image)
    except FileNotFoundError:
        st.error("Model file not found. Place your trained model at model/model.h5 and restart the app.")
        return
    except Exception as exc:
        st.error(f"Prediction failed: {exc}")
        return

    prediction = result.predicted_class
    confidence = result.confidence
    details = get_disease_details(prediction)
    probability_df = pd.DataFrame(
        {"Disease": list(result.probabilities.keys()), "Confidence": list(result.probabilities.values())}
    )

    st.success("Analysis completed successfully")

    st.markdown("<div class='section-title'>Prediction Summary</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Detected Condition", prediction, "Highest probability class")
    with c2:
        metric_card("Confidence", f"{confidence:.2%}", "Model certainty")
    with c3:
        metric_card("Risk Level", details["risk_level"], "Agronomic urgency")

    st.markdown(
        f"""
        <div class="prediction-banner">
            <div>
                <span>AI Diagnosis</span>
                <h2>{prediction}</h2>
                <p>{details["description"]}</p>
            </div>
            <div class="confidence-ring">
                <strong>{confidence:.0%}</strong>
                <small>confidence</small>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    chart_col, table_col = st.columns([1.4, 0.8], gap="large")
    with chart_col:
        st.markdown("<div class='section-title'>Class Probability Chart</div>", unsafe_allow_html=True)
        render_probability_chart(probability_df)
    with table_col:
        st.markdown("<div class='section-title'>Probability Table</div>", unsafe_allow_html=True)
        display_df = probability_df.copy()
        display_df["Confidence"] = display_df["Confidence"].map(lambda value: f"{value:.2%}")
        st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("<div class='section-title'>Disease Intelligence & Recommendations</div>", unsafe_allow_html=True)
    render_solution_cards(details)

    report = build_report(prediction, confidence, probability_df, details)
    st.download_button(
        "Download Prediction Report",
        data=report,
        file_name=f"rice_disease_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain",
        use_container_width=True,
    )


def render_disease_library() -> None:
    st.markdown("<div class='section-title'>Disease Intelligence Library</div>", unsafe_allow_html=True)
    selected = st.selectbox("Select disease", CLASS_NAMES)
    details = get_disease_details(selected)
    st.markdown(
        f"""
        <div class="prediction-banner compact">
            <div>
                <span>{selected}</span>
                <p>{details["description"]}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_solution_cards(details)


def render_history_placeholder() -> None:
    st.markdown("<div class='section-title'>Prediction History</div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="empty-state">
            <strong>History module placeholder</strong>
            <span>Connect a database or CSV log here to track farm-level predictions over time.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    st.markdown(
        """
        <footer>
            RiceAI Disease Detection System | Built for fast screening, farmer guidance, and responsible AI adoption.
        </footer>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    configure_page()
    page = render_sidebar()
    render_hero()

    if page == "Detection Dashboard":
        render_detection_dashboard()
    elif page == "Disease Intelligence":
        render_disease_library()
    else:
        render_history_placeholder()

    render_footer()


if __name__ == "__main__":
    main()
