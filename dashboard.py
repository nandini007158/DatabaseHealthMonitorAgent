import streamlit as st

from database.monitor import run_health_check
from database.monitor import investigate_active_queries
from ai.ai_analyzer import analyze_database_health


# Page configuration
st.set_page_config(
    page_title="Database Health Monitor",
    page_icon="🗄️",
    layout="wide"
)

# Dashboard heading
st.title("AI-Powered Database Health Monitor")
st.caption("MySQL Monitoring | Python | LangGraph | Ollama AI")

st.divider()

# Run database health check
if st.button("Run Database Health Check", type="primary"):

    with st.spinner("Checking database health..."):
        st.session_state.report = run_health_check()
        st.session_state.ai_analysis = None

# Display report
if "report" in st.session_state:

    report = st.session_state.report
    metrics = report["metrics"]

    st.subheader("Database Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Health Score",
        f'{report["health_score"]}/100'
    )

    col2.metric(
        "Database Status",
        report["overall_health"]
    )

    col3.metric(
        "Active Connections",
        metrics.get("active_connections", "N/A")
    )

    st.divider()

    st.subheader("Database Metrics")

    st.write("Database:", metrics.get("database"))
    st.write("Database Size:", metrics.get("database_size_mb"), "MB")
    st.write("Number of Tables:", metrics.get("table_count"))
    st.write("Failed Connections:", metrics.get("failed_connections"))
    st.write("Slow Query Log:", metrics.get("slow_query_log"))

    st.divider()

    st.subheader("Problem Detection")

    problems = report["problems"]

    if problems:
        for problem in problems:
            st.warning(problem)
    else:
        st.success("No monitored problems detected.")

    st.divider()

    # Generate AI analysis
    if st.button("Generate AI Analysis"):

        with st.spinner("Ollama AI is analyzing database metrics..."):

            active_queries = []

            if problems:
                active_queries = investigate_active_queries()

            ai_metrics = metrics.copy()
            ai_metrics["active_query_investigation"] = active_queries

            st.session_state.ai_analysis = analyze_database_health(
                problems,
                report["health_score"],
                ai_metrics
            )

    if st.session_state.get("ai_analysis"):

        st.subheader("AI Analysis and Recommendations")
        st.markdown(st.session_state.ai_analysis)

        st.divider()

        st.subheader("Human Approval")

        st.info(
            "Review the AI recommendations. "
            "No database changes will be executed."
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Approve Recommendations"):
                st.session_state.approval = "APPROVED"

        with col2:
            if st.button("Reject Recommendations"):
                st.session_state.approval = "REJECTED"

        st.write(
            "Approval Status:",
            st.session_state.get("approval", "Not reviewed")
        )

else:
    st.info("Click Run Database Health Check to begin.")