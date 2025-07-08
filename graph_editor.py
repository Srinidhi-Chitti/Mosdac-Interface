# Live-editable NetworkX interface
import streamlit as st
import networkx as nx
from pyvis.network import Network
import tempfile
import os

# Initialize graph in session state
if "G" not in st.session_state:
    st.session_state.G = nx.DiGraph()
    # Preload ISRO mission data
    mission_data = [
        ("Aditya-L1", "PSLV", "solar observation", "ongoing", "launched_by"),
        ("Chandrayaan-3", "LVM3", "lunar landing", "success", "launched_by"),
        ("Gaganyaan", "GSLV Mk III", "crewed spaceflight", "scheduled", "planned_with"),
        ("Mangalyaan", "PSLV", "mars observation", "success", "launched_by"),
        ("XPoSat", "PSLV", "x-ray astronomy", "scheduled", "launched_by"),
        ("RISAT-2B", "PSLV", "earth observation", "success", "launched_by"),
        ("GSAT-11", "GSLV Mk III", "broadband", "success", "launched_by"),
        ("INSAT-3DR", "GSLV", "weather monitoring", "success", "launched_by"),
        ("IRNSS-1G", "PSLV", "navigation", "success", "launched_by"),
        ("SSLV-D2", "SSLV", "small payload launch", "success", "launched_by"),
        ("EOS-06", "PSLV", "remote sensing", "success", "launched_by"),
        ("Cartosat-3", "PSLV", "cartography", "success", "launched_by"),
        ("Astrosat", "PSLV", "space telescope", "success", "launched_by")
    ]
    for mission, vehicle, objective, status, relation in mission_data:
        st.session_state.G.add_node(mission, objective=objective, status=status)
        st.session_state.G.add_edge(mission, vehicle, relation=relation)

def render_graph_editor():
    G = st.session_state.G

    st.subheader("🧠 Knowledge Graph Editor")

    with st.form("Add Node or Relation"):
        col1, col2 = st.columns(2)
        with col1:
            mission = st.text_input("Mission Name")
            objective = st.text_input("Objective")
            status = st.selectbox("Status", ["planned", "ongoing", "success", "failed"])
        with col2:
            vehicle = st.text_input("Launch Vehicle")
            relation = st.selectbox("Relation", ["launched_by", "planned_with", "used_by"])

        submitted = st.form_submit_button("➕ Add to Graph")
        if submitted and mission and vehicle:
            G.add_node(mission, objective=objective, status=status)
            G.add_edge(mission, vehicle, relation=relation)
            st.success(f"Added: {mission} -[{relation}]-> {vehicle}")

    # Visualize with pyvis
    net = Network(height="500px", width="100%", directed=True)
    for node in G.nodes:
        meta = G.nodes[node]
        title = f"Objective: {meta.get('objective')}<br>Status: {meta.get('status')}"
        net.add_node(node, label=node, title=title)
    for u, v, d in G.edges(data=True):
        net.add_edge(u, v, label=d.get("relation", "rel"))

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
        net.show(tmp_file.name, notebook=False)
        html_path = tmp_file.name

    st.components.v1.html(open(html_path, "r", encoding="utf-8").read(), height=550)
    os.unlink(html_path)
