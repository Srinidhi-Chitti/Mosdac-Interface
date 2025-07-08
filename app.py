# === app.py ===
# 🚀 Ultimate ISRO Graph Dashboard – Live, Visual, and Analytical (Enhanced)

import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import json
import re
import datetime
from graph_memory import load_from_txt, enrich_graph_with_missions, graph
from fuzzywuzzy import process

st.set_page_config(page_title="ISRO Knowledge Graph", layout="wide")
st.title("🚀 ISRO Mission Knowledge Graph Dashboard")

# === Help/Info Section ===
st.info("""
**ℹ️ What are these categories?**
- **Mission**: An actual satellite launch or program by ISRO (e.g., Chandrayaan-2, IRNSS-1I).
- **Launch Vehicle**: The rocket used to carry the mission to space (e.g., PSLV-C11, GSLV Mk III).
- **Objective**: The purpose of the mission — Earth observation, lunar landing, climate study, etc.

We automatically tag objectives with categories like "Lunar", "Telecom", or "Climate AI" based on their descriptions.
""")

# === Load & Enrich ===
missions = load_from_txt("isro_missions.txt")
enrich_graph_with_missions(missions)

# === Enhanced Semantic Tagging ===
def enhanced_objective_tags(objective):
    detailed_map = {
        "moon": "Lunar",
        "mars": "Mars",
        "sun": "Solar",
        "solar": "Solar",
        "communication": "Telecom",
        "telecom": "Telecom",
        "disaster": "Disaster Management",
        "climate": "Climate AI",
        "simulation": "Climate AI",
        "x-ray": "Astrophysics",
        "navigation": "Navigation",
        "earth": "Earth Observation",
        "weather": "Meteorology",
        "ecosystem": "Earth Observation",
        "radar": "Remote Sensing",
        "mapping": "Cartography",
        "observation": "Surveillance"
    }
    matches = []
    for keyword, tag in detailed_map.items():
        if re.search(rf"\b{re.escape(keyword)}\b", objective.lower()):
            matches.append(tag)
        else:
            result = process.extractOne(keyword, [objective], score_cutoff=90)
            if result:
                matches.append(tag)
    return sorted(set(matches))

def update_graph_tags():
    for node, data in graph.items():
        if data["type"] == "Objective":
            tags = enhanced_objective_tags(node)
            data["attributes"]["tags"] = tags

update_graph_tags()

# === Sidebar Filters ===
st.sidebar.header("🔍 Filters")
node_type = st.sidebar.selectbox("Node Type", ["All", "Mission", "Launch Vehicle", "Objective"])
tag_filter = st.sidebar.multiselect("Objective Tags", sorted(set(tag for node in graph.values() if node['type'] == 'Objective' for tag in node['attributes'].get("tags", []))))
year_filter = st.sidebar.text_input("Launch Year", "")
search_term = st.sidebar.text_input("Search Keyword (name, tag, or status)", "")

# === Filter Graph ===
G = nx.DiGraph()
for node, data in graph.items():
    if node_type != "All" and data["type"] != node_type:
        continue
    if year_filter and data["type"] == "Mission":
        if year_filter not in str(data["attributes"].get("launch_date", "")):
            continue
    if tag_filter and data["type"] == "Objective":
        node_tags = data["attributes"].get("tags", [])
        if not any(tag in node_tags for tag in tag_filter):
            continue
    if search_term and search_term.lower() not in node.lower():
        tags = data["attributes"].get("tags", [])
        status = data["attributes"].get("status", "")
        if not any(search_term.lower() in t.lower() for t in tags) and search_term.lower() not in status.lower():
            continue
    G.add_node(node, **data)
    for target in data["edges"]:
        if target in graph:
            G.add_edge(node, target)

# === Draw NetworkX Graph ===
if len(G.nodes) > 0:
    fig, ax = plt.subplots(figsize=(18, 12))

    # Choose layout based on node type for better clarity
    if node_type == "Objective":
        pos = nx.shell_layout(G)
    elif node_type == "Launch Vehicle":
        pos = nx.circular_layout(G)
    else:
        pos = nx.spring_layout(G, k=0.8, seed=42)

    # Enhanced visual node styling
    colors = {
        "Mission": "skyblue",
        "Launch Vehicle": "orange",
        "Objective": "lightgreen"
    }
    shapes = {
        "Mission": "o",
        "Launch Vehicle": "s",
        "Objective": "D"
    }

    node_colors = [colors.get(G.nodes[n].get("type", ""), "gray") for n in G.nodes()]
    labels = {n: f"{n}\\n[{G.nodes[n].get('type', '?')}]" for n in G.nodes()}

    nx.draw(G, pos, labels=labels, node_size=1800, node_color=node_colors,
            font_size=8, font_weight="bold", arrows=True, ax=ax)
    st.pyplot(fig)
else:
    st.warning("No data matched the current filters. Try resetting them.")

# === Charts ===
st.subheader("📈 Mission Analytics")
status_counts = {}
vehicle_counts = {}
tag_counts = {}
launch_years = []

for name, data in graph.items():
    if data["type"] == "Mission":
        status = data["attributes"].get("status", "Unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
        date = data["attributes"].get("launch_date", "")
        if date and any(char.isdigit() for char in date):
            match = re.search(r"\d{4}", date)
            if match:
                launch_years.append(int(match.group()))
    if data["type"] == "Launch Vehicle":
        count = sum(1 for n in graph.values() if n["type"] == "Mission" and name in n["edges"])
        vehicle_counts[name] = count
    if data["type"] == "Objective":
        for tag in data["attributes"].get("tags", []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

col1, col2 = st.columns(2)
with col1:
    st.markdown("### ✅ Mission Status Distribution")
    st.bar_chart(pd.Series(status_counts))
with col2:
    st.markdown("### 🚀 Launch Vehicles Used")
    st.bar_chart(pd.Series(vehicle_counts))

st.markdown("### 🎯 Objective Tags")
st.bar_chart(pd.Series(tag_counts))

st.markdown("### 📆 Missions Over Time (Live Growth Rate)")
if launch_years:
    launch_data = pd.Series(launch_years).value_counts().sort_index()
    cumulative = launch_data.cumsum()
    trend = cumulative.diff().fillna(cumulative)
    df = pd.DataFrame({"Missions": launch_data, "Cumulative": cumulative, "Growth Rate": trend})
    st.line_chart(df)
    st.metric("Total Missions", int(cumulative.iloc[-1]))
    st.metric("Avg Growth per Year", round(trend.mean(), 2))
else:
    st.info("No valid launch years found to show trend.")

# === Node Details ===
st.subheader("📋 Node Explorer")
for node, data in graph.items():
    with st.expander(f"{node} ({data['type']})"):
        node_type = data['type']
        attrs = data["attributes"] if data["attributes"] else {}
        edges = data["edges"] if data["edges"] else []

        # Add fallback descriptions for clarity
        if not attrs:
            if node_type == "Mission":
                attrs = {"launch_date": "Unknown", "status": "Unknown"}
            elif node_type == "Launch Vehicle":
                attrs = {"description": "Launch vehicle used in one or more missions."}
            elif node_type == "Objective":
                attrs = {"tags": ["General Objective"]}

        if not edges:
            if node_type == "Mission":
                edges = ["No related vehicle or objective listed."]
            elif node_type == "Launch Vehicle":
                edges = ["Not linked to any mission yet."]
            elif node_type == "Objective":
                edges = ["No missions assigned to this objective."]

        st.json({"Attributes": attrs, "Edges": edges})

# === Export Button ===
st.download_button(
    label="📥 Download Graph as JSON",
    data=json.dumps(graph, indent=2),
    file_name="isro_knowledge_graph.json",
    mime="application/json"
)
