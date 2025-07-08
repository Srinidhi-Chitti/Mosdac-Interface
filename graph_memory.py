# === graph_memory.py ===
# This replaces all Neo4j usage with in-memory structures

# In-memory graph store
graph = {}

def add_node(name, type_, **attrs):
    if name not in graph:
        graph[name] = {"type": type_, "attributes": attrs, "edges": []}
    else:
        graph[name]["attributes"].update(attrs)

def add_relationship(from_node, to_node):
    if from_node in graph and to_node in graph:
        if to_node not in graph[from_node]["edges"]:
            graph[from_node]["edges"].append(to_node)

def query_node(name):
    return graph.get(name, None)

def find_related(node_name):
    if node_name in graph:
        return graph[node_name]["edges"]
    return []

def find_nodes_by_type(type_):
    return [k for k, v in graph.items() if v["type"] == type_]

def print_graph():
    for node, data in graph.items():
        print(f"Node: {node} ({data['type']})")
        print(f"  Attributes: {data['attributes']}")
        print(f"  Edges: {data['edges']}")

# === Replacements for original scripts ===

# graph_agent.py functionality

def get_mission_summary(mission_name):
    node = query_node(mission_name)
    if node and node["type"] == "Mission":
        summary = f"{mission_name} launched on {node['attributes'].get('launch_date', 'unknown date')} with status: {node['attributes'].get('status', 'unknown')}"
        related = find_related(mission_name)
        if related:
            summary += f". Related to: {', '.join(related)}"
        return summary
    return f"No mission found for {mission_name}"

# enrich_graph.py logic replacement

def enrich_graph_with_missions(missions):
    for mission in missions:
        name = mission["Mission"]
        add_node(name, "Mission", 
                 launch_date=mission.get("Launch Date"),
                 status=mission.get("Status"))
        add_node(mission["Launch Vehicle"], "Launch Vehicle")
        add_relationship(name, mission["Launch Vehicle"])

        if "Objective" in mission:
            add_node(mission["Objective"], "Objective")
            add_relationship(name, mission["Objective"])

# seed_data.py logic replacement

def load_from_txt(file_path):
    with open(file_path) as f:
        missions = []
        current = {}
        for line in f:
            line = line.strip()
            if not line:
                if current:
                    missions.append(current)
                    current = {}
            else:
                key, value = line.split(": ", 1)
                current[key.strip()] = value.strip()
        if current:
            missions.append(current)
    return missions

if __name__ == "__main__":
    missions = load_from_txt("isro_missions.txt")
    enrich_graph_with_missions(missions)
    print_graph()
