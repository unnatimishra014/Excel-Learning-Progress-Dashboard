
# ExcelProgressDashboard_UIX_Clean_NoUploader.py
# Install required packages first:
# pip install streamlit pandas matplotlib openpyxl

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------
# Dark theme + bold CSS
# -------------------------
st.markdown("""
    <style>
    /* Dark background */
    .reportview-container {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    /* Sidebar */
    .sidebar .sidebar-content {
        background-color: #2c2c2c;
        color: #ffffff;
        font-weight: bold;
    }
    /* Headers bold */
    h1, h2, h3, h4, h5, h6 {
        font-weight: bold;
        color: #ffffff;
    }
    /* Metric labels bold */
    .stMetric label {
        font-weight: bold;
    }
    /* Table */
    .stDataFrame {
        color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Excel Progress Dashboard", layout="wide")
st.title("📊 Excel Progress Dashboard")
st.markdown("Interactive view of your Excel learning progress with Completed & Ongoing percentages.")

# -------------------------
# STEP 1: Fixed Dataset
# -------------------------
rows = [
    (1, "Excel Sort & Filter", "Excel Sort & Filter Part1", "Sum", 36, "Completed"),
    (1.7, "Excel Sort & Filter", "Excel Sort & Filter Part2", "Connecting data with different options", 38, "Completed"),
    (2, "Functions in Excel", "Sum", "Sumif", 26, "Completed"),
    (3, "Conditional Formatting", "Conditional Formatting", "Greater Than", 18, "Completed"),
    (4, "Data Validation", "Data Validation", "Data Validation Basic", 13, "Completed"),
    (5, "Pivot Table", "Pivot Table", "Pivot Table Basic", 33, "Completed"),
    (6, "Data Analysis", "Data Analysis Part 1", "VLookUp", 46, "Completed"),
    (6.4, "Data Analysis", "Data Analysis Part 2", "Ongoing", None, "Ongoing"),
    (7, "VBA and Macros", "VBA and Macros Part 1", "", None, "Ongoing"),
    (8, "Excel Dashboard", "Excel Dashboard Part 1", "", None, "Ongoing"),
]

df = pd.DataFrame(rows, columns=["SNo", "Topic", "SubTopic", "SubCategory", "TotalTime_mins", "CompletionStatus"])
df = df[df["CompletionStatus"].isin(["Completed", "Ongoing"])]
topic_time = df.groupby("Topic")["TotalTime_mins"].sum(min_count=1).fillna(0)

def compute_stats(group_df):
    total = len(group_df)
    completed = (group_df["CompletionStatus"] == "Completed").sum()
    ongoing = (group_df["CompletionStatus"] == "Ongoing").sum()
    pct_completed = round((completed / total) * 100, 1)
    pct_ongoing = round((ongoing / total) * 100, 1)
    return pd.Series({
        "Subtopics": total,
        "Completed": completed,
        "Ongoing": ongoing,
        "PctCompleted": pct_completed,
        "PctOngoing": pct_ongoing
    })

topic_stats = df.groupby("Topic").apply(compute_stats)
topic_stats["Time_mins"] = topic_time

# -------------------------
# Sidebar Options
# -------------------------
st.sidebar.header("Dashboard Options")
report_view = st.sidebar.radio("Choose Report View", ["Overview", "Topic-wise Progress", "Detailed Table"])
topics = st.sidebar.multiselect("Select Topic(s)", df["Topic"].unique(), df["Topic"].unique())
statuses = st.sidebar.multiselect("Select Status", ["Completed","Ongoing"], ["Completed","Ongoing"])
filtered_df = df[df["Topic"].isin(topics)]
filtered_df = filtered_df[filtered_df["CompletionStatus"].isin(statuses)]

# -------------------------
# Display Views
# -------------------------
if report_view == "Overview":
    st.subheader("📈 Overall Overview")
    total_subs = len(filtered_df)
    completed = (filtered_df["CompletionStatus"] == "Completed").sum()
    ongoing = (filtered_df["CompletionStatus"] == "Ongoing").sum()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Subtopics", total_subs)
        st.metric("Completed Subtopics", completed, f"{round((completed/total_subs)*100,1)}%")
        st.metric("Ongoing Subtopics", ongoing, f"{round((ongoing/total_subs)*100,1)}%")
    with col2:
        fig, ax = plt.subplots(figsize=(6,4))
        topic_time_filtered = filtered_df.groupby("Topic")["TotalTime_mins"].sum(min_count=1).fillna(0)
        ax.bar(topic_time_filtered.index, topic_time_filtered.values, color="#4CAF50")
        ax.set_ylabel("Minutes", color="#ffffff")
        ax.tick_params(axis='x', rotation=45, colors='#ffffff')
        ax.tick_params(axis='y', colors='#ffffff')
        st.pyplot(fig)

        labels = ["Completed","Ongoing"]
        sizes = [completed, ongoing]
        fig2, ax2 = plt.subplots(figsize=(4,4))
        ax2.pie(sizes, labels=labels, autopct="%1.0f%%", startangle=90, colors=["#4CAF50","#FFC107"])
        centre_circle = plt.Circle((0,0),0.70,fc="1e1e1e")
        fig2.gca().add_artist(centre_circle)
        st.pyplot(fig2)

    st.markdown("---")
    st.subheader("✅ Percent Completed per Topic")
    fig3, ax3 = plt.subplots(figsize=(8,4))
    pct_per_topic = topic_stats.loc[topics]["PctCompleted"]
    ax3.barh(pct_per_topic.index, pct_per_topic.values, color="#2196F3")
    for i, v in enumerate(pct_per_topic.values):
        ax3.text(v + 1, i, f"{v:.0f}%", va="center", color="#ffffff", fontweight='bold')
    ax3.set_xlim(0,100)
    ax3.tick_params(axis='x', colors='#ffffff')
    ax3.tick_params(axis='y', colors='#ffffff')
    st.pyplot(fig3)

elif report_view == "Topic-wise Progress":
    st.subheader("📋 Topic-wise Progress Bars")
    for topic in topic_stats.index:
        completed = topic_stats.loc[topic,"Completed"]
        ongoing = topic_stats.loc[topic,"Ongoing"]
        total = topic_stats.loc[topic,"Subtopics"]
        pct_completed = topic_stats.loc[topic,"PctCompleted"]
        pct_ongoing = topic_stats.loc[topic,"PctOngoing"]
        st.write(f"**{topic}**: {completed}/{total} Completed ({pct_completed}%), {ongoing}/{total} Ongoing ({pct_ongoing}%)")
        st.progress(int(pct_completed))

elif report_view == "Detailed Table":
    st.subheader("📄 Detailed Table View")
    st.dataframe(filtered_df.style.set_properties(**{'color': 'white', 'background-color': '#1e1e1e'}))
