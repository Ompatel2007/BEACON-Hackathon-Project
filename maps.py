import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
from shapely.geometry import Point
import math
import copy

ox.settings.log_console = True

start_address = "Tirupporur, Tamil Nadu, India"
end_address   = "Kelambakkam, Tamil Nadu, India"

start_coords = ox.geocode(start_address)
end_coords   = ox.geocode(end_address)

G = ox.graph_from_point(start_coords, dist=8000, network_type="drive")
G = ox.project_graph(G)

start_proj = ox.projection.project_geometry(
    Point(start_coords[1], start_coords[0]),
    to_crs=G.graph["crs"]
)[0]

end_proj = ox.projection.project_geometry(
    Point(end_coords[1], end_coords[0]),
    to_crs=G.graph["crs"]
)[0]

orig = ox.distance.nearest_nodes(G, start_proj.x, start_proj.y)
dest = ox.distance.nearest_nodes(G, end_proj.x, end_proj.y)

# -------------------------
# 4. ORIGINAL ROUTE
# -------------------------
original_route = nx.shortest_path(G, orig, dest, weight="length")

original_length = 0
for u, v in zip(original_route[:-1], original_route[1:]):
    edge_data = G.get_edge_data(u, v)[0]
    original_length += edge_data["length"]

print("Original route distance (km):", round(original_length / 1000, 2))

# -------------------------
# 5. SIMULATE FLOOD ZONE
# -------------------------
flood_center = (12.7350, 80.1950)
flood_radius = 1000  # meters

flood_proj = ox.projection.project_geometry(
    Point(flood_center[1], flood_center[0]),
    to_crs=G.graph["crs"]
)[0]

flood_x, flood_y = flood_proj.x, flood_proj.y

G_disaster = copy.deepcopy(G)

nodes_to_remove = []

for node, data in G_disaster.nodes(data=True):
    dx = data["x"] - flood_x
    dy = data["y"] - flood_y
    if math.sqrt(dx**2 + dy**2) <= flood_radius:
        nodes_to_remove.append(node)

print("Nodes removed due to flood:", len(nodes_to_remove))

G_disaster.remove_nodes_from(nodes_to_remove)

# -------------------------
# 6. SAFE ROUTE
# -------------------------
try:
    safe_route = nx.shortest_path(G_disaster, orig, dest, weight="length")

    safe_length = 0
    for u, v in zip(safe_route[:-1], safe_route[1:]):
        edge_data = G_disaster.get_edge_data(u, v)[0]
        safe_length += edge_data["length"]

    print("Safe route distance (km):", round(safe_length / 1000, 2))

except nx.NetworkXNoPath:
    print("No safe route available.")
    exit()

# -------------------------
# 7. VISUALIZATION
# -------------------------
fig, ax = ox.plot_graph(
    G,
    node_size=0,
    edge_color="#444444",
    bgcolor="black",
    show=False,
    close=False
)

# Original route (yellow)
ox.plot_graph_route(
    G,
    original_route,
    route_color="yellow",
    route_linewidth=4,
    ax=ax,
    show=False,
    close=False
)

# Safe route (cyan)
ox.plot_graph_route(
    G_disaster,
    safe_route,
    route_color="cyan",
    route_linewidth=6,
    ax=ax,
    show=False,
    close=False
)

# Flood zone circle
circle = plt.Circle((flood_x, flood_y), flood_radius, color="red", alpha=0.3)
ax.add_patch(circle)

# Mark start & destination
orig_x = G.nodes[orig]['x']
orig_y = G.nodes[orig]['y']
dest_x = G.nodes[dest]['x']
dest_y = G.nodes[dest]['y']

ax.scatter(orig_x, orig_y, c="lime", s=120, zorder=5)
ax.scatter(dest_x, dest_y, c="white", s=120, zorder=5)

plt.show()
