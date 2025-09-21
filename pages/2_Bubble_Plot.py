import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# Refresh every 2 seconds (2000 ms)
st_autorefresh(interval=2000, key="refresh")

# ------------------ Page Config ------------------
st.set_page_config(layout="wide")

# ------------------ Load and Clean Data ------------------
df = pd.read_csv("./data/HealthServicesData.csv")
df["refArea_clean"] = df["refArea"].apply(lambda x: x.split("/")[-1] if isinstance(x, str) else x)

st.markdown("<h3 style='text-align:center'>Medical Facilities Data in Lebanon</h3>", unsafe_allow_html=True)

# ------------------ CSS for Compact Layout ------------------
st.markdown(
    """
    <style>
    div.stCheckbox {margin-bottom: -5px;}
    div.stCheckbox label {font-size: 0.85rem !important;}
    details summary {font-size: 0.9rem !important; font-weight: 600;}
    .town-box {
        max-height: 200px;
        overflow-y: auto;
        padding-left: 5px;
        border-left: 2px solid #ddd;
        margin-bottom: 5px;
    }
    .sticky-chart {
        position: -webkit-sticky;
        position: sticky;
        top: 0;
        background-color: white;
        z-index: 999;
        padding-bottom: 10px;
        border-bottom: 1px solid #ddd;
    }
    .refarea-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(120px, 1fr));
        gap: 0px 10px;
    }
    .towns-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(100px, 1fr));
        gap: 0px 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ------------------ State Dictionaries ------------------
if "ref_area_selected" not in st.session_state:
    st.session_state.ref_area_selected = {area: True for area in df["refArea_clean"].unique()}
if "town_selection" not in st.session_state:
    st.session_state.town_selection = {}

# ------------------ Step 1: Chart (Sticky at Top) ------------------
with st.container():
    st.markdown('<div class="sticky-chart">', unsafe_allow_html=True)

    selected_areas = [a for a, c in st.session_state.ref_area_selected.items() if c]
    df_area_filtered = df[df["refArea_clean"].isin(selected_areas)]
    selected_towns = [t for t, c in st.session_state.town_selection.items() if c]
    if selected_towns:
        filtered_df = df_area_filtered[df_area_filtered["Town"].isin(selected_towns)]
    else:
        filtered_df = df_area_filtered

    fig = px.scatter(
        filtered_df,
        x="Type and size of medical resources - Hospitals",
        y="Type and size of medical resources - Clinics",
        size="Type and size of medical resources - Pharmacies",
        color="refArea_clean",
        hover_name="Town",
        size_max=60,
        title="Healthcare Resource Distribution in Lebanon - Bubble size refers to the number of pharmacies.",
        labels={"refArea_clean": "Governorate / District"}  
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------ Step 2: RefArea & Towns (Selectors at Bottom) ------------------
col1, col2 = st.columns([1, 2])

# ------------------ RefAreas (2 columns + buttons) ------------------
with col1:
    st.markdown("### Governorate / District")

    # Buttons
    colA, colB = st.columns([1,1])
    with colA:
        if st.button("Check All"):
            for area in df["refArea_clean"].unique():
                st.session_state.ref_area_selected[area] = True
    with colB:
        if st.button("Uncheck All"):
            for area in df["refArea_clean"].unique():
                st.session_state.ref_area_selected[area] = False

    # Checkboxes
    st.markdown('<div class="refarea-grid">', unsafe_allow_html=True)
    for area in df["refArea_clean"].unique():
        st.session_state.ref_area_selected[area] = st.checkbox(
            area,
            value=st.session_state.ref_area_selected.get(area, True),
            key=f"area_{area}"
        )
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------ Towns (3 columns inside each expander) ------------------
with col2:
    st.markdown("### Towns")
    for area in [a for a, c in st.session_state.ref_area_selected.items() if c]:
        towns = df[df["refArea_clean"] == area]["Town"].unique()
        with st.expander(area, expanded=False):
            st.markdown('<div class="town-box towns-grid">', unsafe_allow_html=True)
            for town in towns:
                st.session_state.town_selection[town] = st.checkbox(
                    town,
                    value=st.session_state.town_selection.get(town, True),
                    key=f"town_{area}_{town}"
                )
            st.markdown('</div>', unsafe_allow_html=True)
