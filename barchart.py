import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------ Page Config ------------------
st.set_page_config(layout="wide")

# ------------------ Load and Clean Data ------------------
df = pd.read_csv("data/HealthServicesData.csv")
df["refArea_clean"] = df["refArea"].apply(lambda x: x.split("/")[-1] if isinstance(x, str) else x)

st.markdown("<h3 style='text-align:center'>Medical Facilities Distribution in Lebanon</h3>", unsafe_allow_html=True)

# ------------------ Simplified Facility Names ------------------
facility_map = {
    "Type and size of medical resources - Hospitals": "Hospitals",
    "Type and size of medical resources - Clinics": "Clinics",
    "Type and size of medical resources - Pharmacies": "Pharmacies"
}
facility_columns = [col for col in facility_map if col in df.columns]

# ------------------ Initialize session state for governorates ------------------
if "gov_selected" not in st.session_state:
    st.session_state.gov_selected = {area: True for area in df["refArea_clean"].unique()}

# ------------------ CSS for Sidebar Scrollable Boxes ------------------
st.markdown("""
<style>
.main > div.block-container { padding-left:0rem; padding-right:0rem; max-width:100%; }
div.stCheckbox {margin-bottom:-5px;}
div.stCheckbox label {font-size:0.85rem !important;}
.scroll-box { max-height:300px; overflow-y:auto; padding:5px; border:1px solid #ddd; border-radius:5px; }
</style>
""", unsafe_allow_html=True)

# ------------------ Sidebar Filters ------------------
st.sidebar.header("Filters")

# ---------- Facility Types (single column) ----------
st.sidebar.markdown("**Facility Types**")
selected_facilities = []
st.sidebar.markdown('<div class="scroll-box">', unsafe_allow_html=True)
for i, facility in enumerate(facility_columns):
    short_name = facility_map[facility]
    if st.sidebar.checkbox(short_name, value=True, key=f"fac_{i}"):
        selected_facilities.append(facility)
st.sidebar.markdown('</div>', unsafe_allow_html=True)

# ---------- Governorates / Districts (Check All / Uncheck All + Scrollable) ----------
st.sidebar.markdown("**Governorate / District**")

# Buttons to check/uncheck all
if st.sidebar.button("Check All"):
    for area in st.session_state.gov_selected:
        st.session_state.gov_selected[area] = True
if st.sidebar.button("Uncheck All"):
    for area in st.session_state.gov_selected:
        st.session_state.gov_selected[area] = False

selected_governorates = []
st.sidebar.markdown('<div class="scroll-box">', unsafe_allow_html=True)
for i, area in enumerate(sorted(df["refArea_clean"].unique())):
    st.session_state.gov_selected[area] = st.sidebar.checkbox(
        area,
        value=st.session_state.gov_selected.get(area, True),
        key=f"gov_{i}"
    )
    if st.session_state.gov_selected[area]:
        selected_governorates.append(area)
st.sidebar.markdown('</div>', unsafe_allow_html=True)

# ------------------ Chart on Top ------------------
st.markdown("<h4>Facility Counts by Governorate</h4>", unsafe_allow_html=True)

if selected_facilities and selected_governorates:
    df_filtered = df[df["refArea_clean"].isin(selected_governorates)]
    df_melted = df_filtered.melt(
        id_vars=["refArea_clean", "Town"],
        value_vars=selected_facilities,
        var_name="Facility_Type",
        value_name="Count"
    )
    df_melted = df_melted[df_melted["Count"].notnull() & (df_melted["Count"] > 0)]
    df_melted["Facility_Type"] = df_melted["Facility_Type"].map(facility_map)

    fig = px.bar(
        df_melted,
        x="refArea_clean",
        y="Count",
        color="Facility_Type",
        hover_data=["Town"],
        title="Stacked Bar: Facility Counts by Governorate",
        labels={"refArea_clean": "Governorate / District", "Count": "Number of Facilities", "Facility_Type": "Facility Type"}
    )
    fig.update_layout(
        barmode="stack",
        xaxis_tickangle=-45,
        autosize=True,
        margin=dict(l=0, r=0, t=50, b=50)
    )
    st.plotly_chart(fig, use_container_width=True, key="dynamic_chart")
else:
    st.info("Please select at least one facility type and one governorate/district to display the chart.")
