import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="OLA Ride Insights",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Dark theme CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #1E1A2E; color: #FFFFFF; }
    .stSidebar { background-color: #2D2640; }
    .stSidebar .stSelectbox label, .stSidebar .stMultiSelect label,
    .stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar p { color: #FFFFFF !important; }
    .metric-card {
        background: linear-gradient(135deg, #2D2640, #3D3560);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 1px solid #5B4D71;
        margin-bottom: 10px;
    }
    .metric-value { font-size: 2rem; font-weight: bold; color: #BA73EC; }
    .metric-label { font-size: 0.85rem; color: #CCCCCC; margin-top: 4px; }
    .section-header {
        font-size: 1.3rem; font-weight: bold; color: #BA73EC;
        border-left: 4px solid #BA73EC; padding-left: 12px;
        margin: 20px 0 12px 0;
    }
    .sql-box {
        background-color: #2D2640;
        border: 1px solid #5B4D71;
        border-radius: 8px;
        padding: 14px;
        font-family: monospace;
        font-size: 0.85rem;
        color: #E0D0FF;
        white-space: pre-wrap;
        margin-bottom: 10px;
    }
    div[data-testid="stDataFrame"] { background-color: #2D2640; }
    .stTabs [data-baseweb="tab"] { color: #CCCCCC; background-color: #2D2640; }
    .stTabs [aria-selected="true"] { color: #BA73EC !important; border-bottom: 2px solid #BA73EC; }
    h1, h2, h3 { color: #FFFFFF; }
    .stMarkdown p { color: #CCCCCC; }
    .insight-box {
        background: #2D2640;
        border-left: 3px solid #BA73EC;
        border-radius: 0 8px 8px 0;
        padding: 10px 14px;
        margin: 6px 0;
        color: #E0D0FF;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Load Data ──────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel("OLA_DataSet.xlsx", sheet_name="July")
    df.columns = df.columns.str.strip().str.replace(" ", "_")

    # Fix Date
    df["Date"] = pd.to_datetime(df["Date"]).dt.date

    # Fix Time — handle all possible formats safely
    def parse_time(val):
        try:
            if pd.isna(val):
                return ""
            # Already a time/datetime object
            if hasattr(val, 'strftime'):
                return val.strftime("%H:%M")
            # Numeric (Excel serial fraction)
            if isinstance(val, (int, float)):
                total_seconds = round(float(val) * 86400)
                h = (total_seconds // 3600) % 24
                m = (total_seconds % 3600) // 60
                return f"{h:02d}:{m:02d}"
            # String fallback
            return str(val)[:5]
        except:
            return ""

    df["Time"] = df["Time"].apply(parse_time)

    df["Booking_Value"]  = pd.to_numeric(df["Booking_Value"],  errors="coerce").fillna(0)
    df["Ride_Distance"]  = pd.to_numeric(df["Ride_Distance"],  errors="coerce").fillna(0)
    df["Driver_Ratings"] = pd.to_numeric(df["Driver_Ratings"], errors="coerce")
    df["Customer_Rating"]= pd.to_numeric(df["Customer_Rating"],errors="coerce")
    return df

df = load_data()

PLOTLY_THEME = dict(
    paper_bgcolor="#1E1A2E",
    plot_bgcolor="#2D2640",
    font_color="#CCCCCC",
    title_font_color="#FFFFFF",
)

def styled_fig(fig, title=""):
    fig.update_layout(
        **PLOTLY_THEME,
        title=dict(text=title, font=dict(color="#FFFFFF", size=15)),
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(font=dict(color="#CCCCCC")),
    )
    fig.update_xaxes(tickfont=dict(color="#CCCCCC"), title_font=dict(color="#CCCCCC"), gridcolor="#3D3560")
    fig.update_yaxes(tickfont=dict(color="#CCCCCC"), title_font=dict(color="#CCCCCC"), gridcolor="#3D3560")
    return fig

# ── Sidebar ────────────────────────────────────────────────────────────────────
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Ola_Cabs_logo.svg/320px-Ola_Cabs_logo.svg.png", width=120)
st.sidebar.title("OLA Ride Insights")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["🏠 Overall", "🚘 Vehicle Type", "💰 Revenue", "❌ Cancellation", "⭐ Ratings", "🔍 SQL Queries"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Filters**")
vehicle_filter = st.sidebar.multiselect(
    "Vehicle Type", options=sorted(df["Vehicle_Type"].unique()),
    default=sorted(df["Vehicle_Type"].unique())
)
status_filter = st.sidebar.multiselect(
    "Booking Status", options=sorted(df["Booking_Status"].unique()),
    default=sorted(df["Booking_Status"].unique())
)

dff = df[df["Vehicle_Type"].isin(vehicle_filter) & df["Booking_Status"].isin(status_filter)]

# ── PAGE 1: OVERALL ────────────────────────────────────────────────────────────
if page == "🏠 Overall":
    st.markdown("<h1 style='color:#BA73EC;'>🚗 OLA Ride Insights — Overall</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#CCCCCC;'>July 2024 | Bangalore Operations</p>", unsafe_allow_html=True)

    total       = len(dff)
    success     = len(dff[dff["Booking_Status"] == "Success"])
    revenue     = dff[dff["Booking_Status"] == "Success"]["Booking_Value"].sum()
    avg_dist    = dff[dff["Booking_Status"] == "Success"]["Ride_Distance"].mean()
    cancel_rate = len(dff[dff["Booking_Status"].str.contains("Cancel", na=False)]) / total * 100

    c1, c2, c3, c4, c5 = st.columns(5)
    for col, val, label in zip(
        [c1, c2, c3, c4, c5],
        [f"{total:,}", f"{success:,}", f"₹{revenue/1e6:.2f}M", f"{avg_dist:.1f} km", f"{cancel_rate:.1f}%"],
        ["Total Bookings", "Successful Rides", "Total Revenue", "Avg Ride Distance", "Cancellation Rate"]
    ):
        col.markdown(f"""<div class='metric-card'>
            <div class='metric-value'>{val}</div>
            <div class='metric-label'>{label}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='section-header'>Booking Status Breakdown</div>", unsafe_allow_html=True)
        status_df = dff["Booking_Status"].value_counts().reset_index()
        status_df.columns = ["Status", "Count"]
        fig = px.pie(status_df, names="Status", values="Count",
                     color_discrete_sequence=["#BA73EC","#5B4D71","#E66C37","#D64550"])
        st.plotly_chart(styled_fig(fig), use_container_width=True)

    with col2:
        st.markdown("<div class='section-header'>Daily Ride Volume — July 2024</div>", unsafe_allow_html=True)
        daily = dff.groupby("Date").size().reset_index(name="Rides")
        daily["Date"] = pd.to_datetime(daily["Date"])
        fig2 = px.line(daily, x="Date", y="Rides", markers=True,
                       color_discrete_sequence=["#BA73EC"])
        st.plotly_chart(styled_fig(fig2), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("<div class='section-header'>Revenue by Date</div>", unsafe_allow_html=True)
        rev_daily = dff[dff["Booking_Status"]=="Success"].groupby("Date")["Booking_Value"].sum().reset_index()
        rev_daily["Date"] = pd.to_datetime(rev_daily["Date"])
        fig3 = px.area(rev_daily, x="Date", y="Booking_Value",
                       color_discrete_sequence=["#BA73EC"])
        fig3.update_traces(fillcolor="rgba(186,115,236,0.2)")
        st.plotly_chart(styled_fig(fig3), use_container_width=True)

    with col4:
        st.markdown("<div class='section-header'>Bookings by Vehicle Type</div>", unsafe_allow_html=True)
        veh_df = dff["Vehicle_Type"].value_counts().reset_index()
        veh_df.columns = ["Vehicle", "Count"]
        fig4 = px.bar(veh_df, x="Count", y="Vehicle", orientation="h",
                      color="Count", color_continuous_scale=["#5B4D71","#BA73EC"])
        st.plotly_chart(styled_fig(fig4), use_container_width=True)

    st.markdown("<div class='section-header'>Key Insights</div>", unsafe_allow_html=True)
    for insight in [
        f"✅ {success:,} out of {total:,} rides were successful — a {success/total*100:.1f}% success rate.",
        f"📅 Data covers July 2024 with {daily['Rides'].max():,} rides on the busiest day.",
        f"❌ {cancel_rate:.1f}% cancellation rate — a key area for operational improvement.",
        f"💰 Total revenue from successful rides: ₹{revenue/1e6:.2f}M"
    ]:
        st.markdown(f"<div class='insight-box'>{insight}</div>", unsafe_allow_html=True)

# ── PAGE 2: VEHICLE TYPE ───────────────────────────────────────────────────────
elif page == "🚘 Vehicle Type":
    st.markdown("<h1 style='color:#BA73EC;'>🚘 Vehicle Type Analysis</h1>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='section-header'>Avg Ride Distance by Vehicle</div>", unsafe_allow_html=True)
        avg_d = dff.groupby("Vehicle_Type")["Ride_Distance"].mean().reset_index().sort_values("Ride_Distance", ascending=True)
        fig = px.bar(avg_d, x="Ride_Distance", y="Vehicle_Type", orientation="h",
                     color="Ride_Distance", color_continuous_scale=["#5B4D71","#BA73EC"],
                     labels={"Ride_Distance":"Avg Distance (km)"})
        st.plotly_chart(styled_fig(fig), use_container_width=True)

    with col2:
        st.markdown("<div class='section-header'>Booking Count by Vehicle</div>", unsafe_allow_html=True)
        cnt = dff["Vehicle_Type"].value_counts().reset_index()
        cnt.columns = ["Vehicle", "Count"]
        fig2 = px.bar(cnt.sort_values("Count"), x="Count", y="Vehicle", orientation="h",
                      color="Count", color_continuous_scale=["#5B4D71","#BA73EC"])
        st.plotly_chart(styled_fig(fig2), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("<div class='section-header'>Revenue by Vehicle Type</div>", unsafe_allow_html=True)
        rev_v = dff[dff["Booking_Status"]=="Success"].groupby("Vehicle_Type")["Booking_Value"].sum().reset_index().sort_values("Booking_Value")
        fig3 = px.bar(rev_v, x="Booking_Value", y="Vehicle_Type", orientation="h",
                      color="Booking_Value", color_continuous_scale=["#5B4D71","#BA73EC"],
                      labels={"Booking_Value":"Total Revenue (₹)"})
        st.plotly_chart(styled_fig(fig3), use_container_width=True)

    with col4:
        st.markdown("<div class='section-header'>Vehicle Type Share</div>", unsafe_allow_html=True)
        fig4 = px.pie(cnt, names="Vehicle", values="Count",
                      color_discrete_sequence=["#BA73EC","#5B4D71","#E66C37","#6B007B","#E044A7","#744EC2","#D9B300"])
        st.plotly_chart(styled_fig(fig4), use_container_width=True)

    st.markdown("<div class='section-header'>Vehicle Summary Table</div>", unsafe_allow_html=True)
    summary = dff.groupby("Vehicle_Type").agg(
        Total_Bookings=("Booking_ID","count"),
        Successful=("Booking_Status", lambda x: (x=="Success").sum()),
        Avg_Distance=("Ride_Distance","mean"),
        Avg_Driver_Rating=("Driver_Ratings","mean"),
        Avg_Customer_Rating=("Customer_Rating","mean"),
        Total_Revenue=("Booking_Value","sum")
    ).round(2).reset_index()
    st.dataframe(summary.style.background_gradient(cmap="Purples"), use_container_width=True)

# ── PAGE 3: REVENUE ────────────────────────────────────────────────────────────
elif page == "💰 Revenue":
    st.markdown("<h1 style='color:#BA73EC;'>💰 Revenue Analysis</h1>", unsafe_allow_html=True)

    success_df = dff[dff["Booking_Status"] == "Success"]
    total_rev = success_df["Booking_Value"].sum()
    avg_rev   = success_df["Booking_Value"].mean()
    max_rev   = success_df["Booking_Value"].max()

    c1, c2, c3 = st.columns(3)
    for col, val, label in zip(
        [c1, c2, c3],
        [f"₹{total_rev/1e6:.2f}M", f"₹{avg_rev:.0f}", f"₹{max_rev:.0f}"],
        ["Total Revenue", "Avg per Ride", "Highest Single Ride"]
    ):
        col.markdown(f"<div class='metric-card'><div class='metric-value'>{val}</div><div class='metric-label'>{label}</div></div>", unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='section-header'>Revenue by Payment Method</div>", unsafe_allow_html=True)
        pay = success_df.groupby("Payment_Method")["Booking_Value"].sum().reset_index().sort_values("Booking_Value", ascending=False)
        fig = px.bar(pay, x="Payment_Method", y="Booking_Value",
                     color="Booking_Value", color_continuous_scale=["#5B4D71","#BA73EC"],
                     labels={"Booking_Value":"Revenue (₹)"})
        st.plotly_chart(styled_fig(fig), use_container_width=True)

    with col2:
        st.markdown("<div class='section-header'>Payment Method Usage Count</div>", unsafe_allow_html=True)
        pay_cnt = success_df["Payment_Method"].value_counts().reset_index()
        pay_cnt.columns = ["Method","Count"]
        fig2 = px.pie(pay_cnt, names="Method", values="Count",
                      color_discrete_sequence=["#BA73EC","#5B4D71","#E66C37","#6B007B"])
        st.plotly_chart(styled_fig(fig2), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("<div class='section-header'>Top 10 Customers by Revenue</div>", unsafe_allow_html=True)
        top_cust = success_df.groupby("Customer_ID")["Booking_Value"].sum().nlargest(10).reset_index()
        top_cust.columns = ["Customer","Revenue"]
        fig3 = px.bar(top_cust.sort_values("Revenue"), x="Revenue", y="Customer", orientation="h",
                      color="Revenue", color_continuous_scale=["#5B4D71","#BA73EC"])
        st.plotly_chart(styled_fig(fig3), use_container_width=True)

    with col4:
        st.markdown("<div class='section-header'>Revenue by Vehicle Type</div>", unsafe_allow_html=True)
        rev_v = success_df.groupby("Vehicle_Type")["Booking_Value"].sum().reset_index()
        fig4 = px.pie(rev_v, names="Vehicle_Type", values="Booking_Value",
                      color_discrete_sequence=["#BA73EC","#5B4D71","#E66C37","#6B007B","#E044A7","#744EC2","#D9B300"])
        st.plotly_chart(styled_fig(fig4), use_container_width=True)

    st.markdown("<div class='section-header'>Revenue Trend — July 2024</div>", unsafe_allow_html=True)
    rev_daily = success_df.groupby("Date")["Booking_Value"].sum().reset_index()
    rev_daily["Date"] = pd.to_datetime(rev_daily["Date"])
    fig5 = px.area(rev_daily, x="Date", y="Booking_Value",
                   color_discrete_sequence=["#BA73EC"],
                   labels={"Booking_Value":"Revenue (₹)"})
    fig5.update_traces(fillcolor="rgba(186,115,236,0.15)")
    st.plotly_chart(styled_fig(fig5), use_container_width=True)

# ── PAGE 4: CANCELLATION ───────────────────────────────────────────────────────
elif page == "❌ Cancellation":
    st.markdown("<h1 style='color:#BA73EC;'>❌ Cancellation Analysis</h1>", unsafe_allow_html=True)

    cust_cancel = len(df[df["Booking_Status"] == "Canceled by Customer"])
    drv_cancel  = len(df[df["Booking_Status"] == "Canceled by Driver"])
    not_found   = len(df[df["Booking_Status"] == "Driver Not Found"])
    total_cancel = cust_cancel + drv_cancel + not_found

    c1, c2, c3, c4 = st.columns(4)
    for col, val, label in zip(
        [c1, c2, c3, c4],
        [f"{total_cancel:,}", f"{cust_cancel:,}", f"{drv_cancel:,}", f"{not_found:,}"],
        ["Total Cancellations", "By Customer", "By Driver", "Driver Not Found"]
    ):
        col.markdown(f"<div class='metric-card'><div class='metric-value'>{val}</div><div class='metric-label'>{label}</div></div>", unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='section-header'>Customer Cancellation Reasons</div>", unsafe_allow_html=True)
        cust_reasons = df["Canceled_Rides_by_Customer"].dropna().value_counts().reset_index()
        cust_reasons.columns = ["Reason","Count"]
        fig = px.bar(cust_reasons, x="Count", y="Reason", orientation="h",
                     color="Count", color_continuous_scale=["#5B4D71","#E66C37"])
        st.plotly_chart(styled_fig(fig), use_container_width=True)

    with col2:
        st.markdown("<div class='section-header'>Driver Cancellation Reasons</div>", unsafe_allow_html=True)
        drv_reasons = df["Canceled_Rides_by_Driver"].dropna().value_counts().reset_index()
        drv_reasons.columns = ["Reason","Count"]
        fig2 = px.bar(drv_reasons, x="Count", y="Reason", orientation="h",
                      color="Count", color_continuous_scale=["#5B4D71","#BA73EC"])
        st.plotly_chart(styled_fig(fig2), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("<div class='section-header'>Cancellation by Vehicle Type</div>", unsafe_allow_html=True)
        cancel_veh = df[df["Booking_Status"].str.contains("Cancel", na=False)].groupby("Vehicle_Type").size().reset_index(name="Cancellations")
        fig3 = px.pie(cancel_veh, names="Vehicle_Type", values="Cancellations",
                      color_discrete_sequence=["#BA73EC","#5B4D71","#E66C37","#6B007B","#E044A7","#744EC2","#D9B300"])
        st.plotly_chart(styled_fig(fig3), use_container_width=True)

    with col4:
        st.markdown("<div class='section-header'>Booking Status Distribution</div>", unsafe_allow_html=True)
        status_all = df["Booking_Status"].value_counts().reset_index()
        status_all.columns = ["Status","Count"]
        fig4 = px.bar(status_all, x="Status", y="Count",
                      color="Count", color_continuous_scale=["#5B4D71","#BA73EC"])
        st.plotly_chart(styled_fig(fig4), use_container_width=True)

    st.markdown("<div class='section-header'>Key Insights</div>", unsafe_allow_html=True)
    top_cust_reason = df["Canceled_Rides_by_Customer"].dropna().value_counts().index[0]
    top_drv_reason  = df["Canceled_Rides_by_Driver"].dropna().value_counts().index[0]
    for insight in [
        f"🚗 Top customer cancellation reason: '{top_cust_reason}' ({df['Canceled_Rides_by_Customer'].value_counts().iloc[0]:,} times)",
        f"👨‍✈️ Top driver cancellation reason: '{top_drv_reason}' ({df['Canceled_Rides_by_Driver'].value_counts().iloc[0]:,} times)",
        f"🔍 {not_found:,} rides had no driver found — potential supply-demand mismatch.",
    ]:
        st.markdown(f"<div class='insight-box'>{insight}</div>", unsafe_allow_html=True)

# ── PAGE 5: RATINGS ────────────────────────────────────────────────────────────
elif page == "⭐ Ratings":
    st.markdown("<h1 style='color:#BA73EC;'>⭐ Ratings Analysis</h1>", unsafe_allow_html=True)

    rated    = df[df["Booking_Status"] == "Success"]
    avg_drv  = rated["Driver_Ratings"].mean()
    avg_cust = rated["Customer_Rating"].mean()
    max_drv  = rated["Driver_Ratings"].max()
    min_drv  = rated["Driver_Ratings"].min()

    c1, c2, c3, c4 = st.columns(4)
    for col, val, label in zip(
        [c1, c2, c3, c4],
        [f"{avg_drv:.2f} ⭐", f"{avg_cust:.2f} ⭐", f"{max_drv:.1f}", f"{min_drv:.1f}"],
        ["Avg Driver Rating", "Avg Customer Rating", "Highest Driver Rating", "Lowest Driver Rating"]
    ):
        col.markdown(f"<div class='metric-card'><div class='metric-value'>{val}</div><div class='metric-label'>{label}</div></div>", unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='section-header'>Avg Driver Rating by Vehicle</div>", unsafe_allow_html=True)
        drv_veh = rated.groupby("Vehicle_Type")["Driver_Ratings"].mean().reset_index().sort_values("Driver_Ratings")
        fig = px.bar(drv_veh, x="Driver_Ratings", y="Vehicle_Type", orientation="h",
                     color="Driver_Ratings", color_continuous_scale=["#5B4D71","#BA73EC"],
                     range_x=[3.5, 4.5])
        st.plotly_chart(styled_fig(fig), use_container_width=True)

    with col2:
        st.markdown("<div class='section-header'>Avg Customer Rating by Vehicle</div>", unsafe_allow_html=True)
        cust_veh = rated.groupby("Vehicle_Type")["Customer_Rating"].mean().reset_index().sort_values("Customer_Rating")
        fig2 = px.bar(cust_veh, x="Customer_Rating", y="Vehicle_Type", orientation="h",
                      color="Customer_Rating", color_continuous_scale=["#5B4D71","#E66C37"],
                      range_x=[3.5, 4.5])
        st.plotly_chart(styled_fig(fig2), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("<div class='section-header'>Driver Ratings Distribution</div>", unsafe_allow_html=True)
        fig3 = px.histogram(rated.dropna(subset=["Driver_Ratings"]), x="Driver_Ratings", nbins=20,
                            color_discrete_sequence=["#BA73EC"])
        st.plotly_chart(styled_fig(fig3), use_container_width=True)

    with col4:
        st.markdown("<div class='section-header'>Driver vs Customer Ratings</div>", unsafe_allow_html=True)
        scatter_df = rated.dropna(subset=["Driver_Ratings","Customer_Rating"])
        fig4 = px.scatter(scatter_df, x="Driver_Ratings", y="Customer_Rating",
                          color="Vehicle_Type", opacity=0.5,
                          color_discrete_sequence=["#BA73EC","#5B4D71","#E66C37","#6B007B","#E044A7","#744EC2","#D9B300"])
        st.plotly_chart(styled_fig(fig4), use_container_width=True)

    st.markdown("<div class='section-header'>Prime Sedan — Driver Rating Range</div>", unsafe_allow_html=True)
    prime = rated[rated["Vehicle_Type"] == "Prime Sedan"]["Driver_Ratings"].dropna()
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"<div class='metric-card'><div class='metric-value'>{prime.max():.1f} ⭐</div><div class='metric-label'>Max Rating</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='metric-card'><div class='metric-value'>{prime.min():.1f} ⭐</div><div class='metric-label'>Min Rating</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='metric-card'><div class='metric-value'>{prime.mean():.2f} ⭐</div><div class='metric-label'>Avg Rating</div></div>", unsafe_allow_html=True)

# ── PAGE 6: SQL QUERIES ────────────────────────────────────────────────────────
elif page == "🔍 SQL Queries":
    st.markdown("<h1 style='color:#BA73EC;'>🔍 SQL Query Results</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#CCCCCC;'>All 10 required queries — executed live on the dataset</p>", unsafe_allow_html=True)

    QUERIES = {
        "Q1 — All Successful Bookings": {
            "sql": "SELECT * FROM bookings\nWHERE Booking_Status = 'Success'",
            "fn": lambda d: d[d["Booking_Status"] == "Success"]
        },
        "Q2 — Avg Ride Distance by Vehicle Type": {
            "sql": "SELECT Vehicle_Type, ROUND(AVG(Ride_Distance), 2) AS avg_distance\nFROM bookings\nGROUP BY Vehicle_Type\nORDER BY avg_distance DESC",
            "fn": lambda d: d.groupby("Vehicle_Type")["Ride_Distance"].mean().round(2).reset_index().rename(columns={"Ride_Distance":"avg_distance"}).sort_values("avg_distance", ascending=False)
        },
        "Q3 — Total Customer Cancellations": {
            "sql": "SELECT COUNT(*) AS total_cancelled\nFROM bookings\nWHERE Booking_Status = 'Canceled by Customer'",
            "fn": lambda d: pd.DataFrame({"total_cancelled": [len(d[d["Booking_Status"] == "Canceled by Customer"])]})
        },
        "Q4 — Top 5 Customers by Rides": {
            "sql": "SELECT Customer_ID, COUNT(*) AS total_rides\nFROM bookings\nGROUP BY Customer_ID\nORDER BY total_rides DESC\nLIMIT 5",
            "fn": lambda d: d.groupby("Customer_ID").size().nlargest(5).reset_index(name="total_rides")
        },
        "Q5 — Driver Cancels: Personal/Car Issue": {
            "sql": "SELECT COUNT(*) AS total\nFROM bookings\nWHERE Canceled_Rides_by_Driver = 'Personal & Car related issue'",
            "fn": lambda d: pd.DataFrame({"total": [len(d[d["Canceled_Rides_by_Driver"] == "Personal & Car related issue"])]})
        },
        "Q6 — Prime Sedan Driver Rating Range": {
            "sql": "SELECT MAX(Driver_Ratings) AS max_rating,\n       MIN(Driver_Ratings) AS min_rating\nFROM bookings\nWHERE Vehicle_Type = 'Prime Sedan'",
            "fn": lambda d: pd.DataFrame({
                "max_rating": [d[d["Vehicle_Type"]=="Prime Sedan"]["Driver_Ratings"].max()],
                "min_rating": [d[d["Vehicle_Type"]=="Prime Sedan"]["Driver_Ratings"].min()]
            })
        },
        "Q7 — All UPI Payment Rides": {
            "sql": "SELECT * FROM bookings\nWHERE Payment_Method = 'UPI'",
            "fn": lambda d: d[d["Payment_Method"] == "UPI"]
        },
        "Q8 — Avg Customer Rating by Vehicle": {
            "sql": "SELECT Vehicle_Type, ROUND(AVG(Customer_Rating), 2) AS avg_rating\nFROM bookings\nGROUP BY Vehicle_Type\nORDER BY avg_rating DESC",
            "fn": lambda d: d.groupby("Vehicle_Type")["Customer_Rating"].mean().round(2).reset_index().rename(columns={"Customer_Rating":"avg_rating"}).sort_values("avg_rating", ascending=False)
        },
        "Q9 — Total Revenue from Successful Rides": {
            "sql": "SELECT SUM(Booking_Value) AS total_revenue\nFROM bookings\nWHERE Booking_Status = 'Success'",
            "fn": lambda d: pd.DataFrame({"total_revenue": [d[d["Booking_Status"]=="Success"]["Booking_Value"].sum()]})
        },
        "Q10 — Incomplete Rides with Reasons": {
            "sql": "SELECT Booking_ID, Vehicle_Type, Pickup_Location,\n       Drop_Location, Incomplete_Rides_Reason\nFROM bookings\nWHERE Incomplete_Rides = 'Yes'",
            "fn": lambda d: d[d["Incomplete_Rides"]=="Yes"][["Booking_ID","Vehicle_Type","Pickup_Location","Drop_Location","Incomplete_Rides_Reason"]]
        },
    }

    selected_q = st.selectbox("Select a Query to Run", list(QUERIES.keys()))
    q = QUERIES[selected_q]
    st.markdown(f"<div class='sql-box'>{q['sql']}</div>", unsafe_allow_html=True)
    result = q["fn"](df)
    st.markdown(f"<p style='color:#BA73EC;'>→ {len(result):,} rows returned</p>", unsafe_allow_html=True)
    st.dataframe(result.head(100), use_container_width=True)

    if st.checkbox("Run All 10 Queries at Once"):
        for qname, qdata in QUERIES.items():
            with st.expander(qname):
                st.markdown(f"<div class='sql-box'>{qdata['sql']}</div>", unsafe_allow_html=True)
                res = qdata["fn"](df)
                st.dataframe(res.head(50), use_container_width=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("<p style='color:#5B4D71; text-align:center; font-size:0.8rem;'>OLA Ride Insights | July 2024 | Built with Streamlit & Plotly</p>", unsafe_allow_html=True)