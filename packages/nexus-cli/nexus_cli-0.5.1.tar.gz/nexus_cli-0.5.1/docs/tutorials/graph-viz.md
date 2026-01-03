# Graph Visualization Tutorial

Learn how to generate and visualize your knowledge graph from your Obsidian vault using Nexus CLI.

## What is a Knowledge Graph?

A knowledge graph represents:
- **Nodes**: Your notes
- **Edges**: Links between notes (`[[WikiLinks]]`)
- **Communities**: Clusters of related concepts
- **Structure**: The organization of your knowledge

## Prerequisites

- Obsidian vault configured with Nexus
- Notes with `[[WikiLinks]]` connections
- Basic understanding of JSON (helpful but not required)

## Step 1: Generate Graph Data

### Basic Graph

```bash
nexus knowledge vault graph --json > graph.json
```

This creates a JSON file with:
- All notes as nodes
- All `[[WikiLinks]]` as edges
- Metadata for each note

### Include Tags

```bash
nexus knowledge vault graph --tags --json > graph-with-tags.json
```

This adds:
- Tag nodes (e.g., `#statistics`, `#causal-inference`)
- Edges from notes to their tags

### Limit Graph Size

For large vaults (1000+ notes), limit to the most connected:

```bash
# Top 100 most connected notes
nexus knowledge vault graph --limit 100 --json > core-graph.json

# Top 50 with tags
nexus knowledge vault graph --limit 50 --tags --json > core-tags.json
```

### Get Statistics Only

```bash
nexus knowledge vault graph --stats
```

Output:
```
Graph Statistics
─────────────────────────────────────

Nodes: 342
Edges: 1,247
Density: 0.021
Avg connections per node: 3.6

Most connected nodes:
  1. Causal Inference (45 connections)
  2. Mediation Analysis (32 connections)
  3. Statistical Power (28 connections)
  4. Regression Analysis (24 connections)
  5. Bootstrap Methods (21 connections)
```

## Step 2: Understanding the JSON Format

The graph JSON has this structure:

```json
{
  "nodes": [
    {
      "id": "Causal Inference",
      "label": "Causal Inference",
      "type": "note",
      "path": "Concepts/Causal Inference.md",
      "connections": 45,
      "tags": ["statistics", "theory"]
    },
    ...
  ],
  "edges": [
    {
      "source": "Causal Inference",
      "target": "Mediation Analysis",
      "weight": 3
    },
    ...
  ]
}
```

**Fields**:
- `id`: Unique identifier (note title)
- `label`: Display name
- `type`: `note` or `tag`
- `path`: Relative path in vault
- `connections`: Number of links
- `weight`: Number of times two notes link to each other

## Step 3: Visualize in Obsidian

The easiest way to visualize is using Obsidian's built-in graph view:

1. Open your vault in Obsidian
2. Click the graph icon in the left sidebar
3. Use filters to focus on specific areas

**Obsidian Graph Features**:
- Interactive: Click nodes to open notes
- Filters: Show/hide by tags, folders, links
- Coloring: Color code by tags or folders
- Forces: Adjust repulsion, attraction, centering

## Step 4: Visualize with Python

### Option A: NetworkX + Matplotlib

```python
import json
import networkx as nx
import matplotlib.pyplot as plt

# Load graph
with open('graph.json') as f:
    data = json.load(f)

# Create NetworkX graph
G = nx.Graph()

# Add nodes with attributes
for node in data['nodes']:
    G.add_node(node['id'], **node)

# Add edges with weights
for edge in data['edges']:
    G.add_edge(edge['source'], edge['target'], weight=edge.get('weight', 1))

# Calculate layout
pos = nx.spring_layout(G, k=0.5, iterations=50)

# Draw
plt.figure(figsize=(20, 20))

# Size nodes by connections
sizes = [G.nodes[node].get('connections', 1) * 10 for node in G.nodes()]

nx.draw_networkx_nodes(G, pos, node_size=sizes, node_color='lightblue', alpha=0.7)
nx.draw_networkx_edges(G, pos, alpha=0.2)
nx.draw_networkx_labels(G, pos, font_size=8)

plt.axis('off')
plt.tight_layout()
plt.savefig('knowledge-graph.png', dpi=300, bbox_inches='tight')
plt.show()
```

### Option B: Pyvis Interactive HTML

```python
import json
from pyvis.network import Network

# Load graph
with open('graph.json') as f:
    data = json.load(f)

# Create network
net = Network(height='800px', width='100%', bgcolor='#222222', font_color='white')

# Add nodes
for node in data['nodes']:
    net.add_node(
        node['id'],
        label=node['label'],
        title=node.get('path', ''),
        size=node.get('connections', 1) * 2,
        color='#3B82F6' if node['type'] == 'note' else '#F59E0B'
    )

# Add edges
for edge in data['edges']:
    net.add_edge(
        edge['source'],
        edge['target'],
        value=edge.get('weight', 1)
    )

# Configure physics
net.set_options('''
{
  "physics": {
    "forceAtlas2Based": {
      "gravitationalConstant": -50,
      "centralGravity": 0.01,
      "springLength": 100
    },
    "maxVelocity": 50,
    "solver": "forceAtlas2Based"
  }
}
''')

net.show('knowledge-graph.html')
print("Graph saved to knowledge-graph.html")
```

Run it:
```bash
python visualize_graph.py
# Opens interactive graph in browser
```

## Step 5: Visualize with D3.js

Create `graph.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body { margin: 0; background: #1a1a1a; }
        svg { width: 100vw; height: 100vh; }
        .node { cursor: pointer; }
        .node circle { fill: #3B82F6; stroke: #fff; stroke-width: 2px; }
        .node text { fill: #fff; font: 10px sans-serif; }
        .link { stroke: #999; stroke-opacity: 0.6; }
    </style>
</head>
<body>
    <svg id="graph"></svg>
    <script>
    d3.json('graph.json').then(data => {
        const width = window.innerWidth;
        const height = window.innerHeight;
        
        const svg = d3.select('#graph');
        
        const simulation = d3.forceSimulation(data.nodes)
            .force('link', d3.forceLink(data.edges).id(d => d.id))
            .force('charge', d3.forceManyBody().strength(-100))
            .force('center', d3.forceCenter(width / 2, height / 2));
        
        const link = svg.append('g')
            .selectAll('line')
            .data(data.edges)
            .join('line')
            .attr('class', 'link')
            .attr('stroke-width', d => Math.sqrt(d.weight || 1));
        
        const node = svg.append('g')
            .selectAll('g')
            .data(data.nodes)
            .join('g')
            .attr('class', 'node')
            .call(d3.drag()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended));
        
        node.append('circle')
            .attr('r', d => Math.sqrt(d.connections || 1) * 2);
        
        node.append('text')
            .text(d => d.label)
            .attr('x', 12)
            .attr('y', 3);
        
        node.append('title')
            .text(d => `${d.label}\n${d.connections} connections`);
        
        simulation.on('tick', () => {
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);
            
            node.attr('transform', d => `translate(${d.x},${d.y})`);
        });
        
        function dragstarted(event) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        }
        
        function dragged(event) {
            event.subject.fx = event.x;
            event.subject.fy = event.y;
        }
        
        function dragended(event) {
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        }
    });
    </script>
</body>
</html>
```

View it:
```bash
# In the directory with graph.json and graph.html
python -m http.server 8000
# Open http://localhost:8000/graph.html
```

## Step 6: Analysis and Insights

### Find Central Concepts

```python
import json
import networkx as nx

with open('graph.json') as f:
    data = json.load(f)

G = nx.Graph()
for node in data['nodes']:
    G.add_node(node['id'], **node)
for edge in data['edges']:
    G.add_edge(edge['source'], edge['target'])

# Centrality measures
betweenness = nx.betweenness_centrality(G)
closeness = nx.closeness_centrality(G)
pagerank = nx.pagerank(G)

# Top 10 by PageRank
top_nodes = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:10]

print("Most important concepts:")
for node, score in top_nodes:
    print(f"  {node}: {score:.4f}")
```

### Detect Communities

```python
import community  # python-louvain package

# Detect communities
communities = community.best_partition(G)

# Group by community
from collections import defaultdict
community_groups = defaultdict(list)
for node, comm_id in communities.items():
    community_groups[comm_id].append(node)

# Print communities
for comm_id, nodes in community_groups.items():
    print(f"\nCommunity {comm_id} ({len(nodes)} nodes):")
    print("  " + ", ".join(nodes[:5]))
    if len(nodes) > 5:
        print(f"  ... and {len(nodes) - 5} more")
```

### Find Shortest Paths

```python
# Path between two concepts
path = nx.shortest_path(G, "Causal Inference", "Statistical Power")
print("Path:", " → ".join(path))

# Average path length
avg_path = nx.average_shortest_path_length(G)
print(f"Average path length: {avg_path:.2f}")
```

## Advanced Techniques

### Time-based Visualization

Filter by note modification time:

```python
import os
from datetime import datetime, timedelta

# Get notes modified in last 30 days
cutoff = datetime.now() - timedelta(days=30)
recent_nodes = []

for node in data['nodes']:
    path = os.path.join(vault_path, node['path'])
    if os.path.exists(path):
        mtime = datetime.fromtimestamp(os.path.getmtime(path))
        if mtime > cutoff:
            recent_nodes.append(node['id'])

# Filter graph to recent nodes
G_recent = G.subgraph(recent_nodes)
```

### Export to Other Formats

```python
# Export to GraphML (for Gephi, Cytoscape)
nx.write_graphml(G, 'graph.graphml')

# Export to GML
nx.write_gml(G, 'graph.gml')

# Export to DOT (for Graphviz)
nx.drawing.nx_pydot.write_dot(G, 'graph.dot')
```

## Troubleshooting

### "Graph is empty"

Your notes don't have `[[WikiLinks]]` yet. Add some connections:

```markdown
# Mediation Analysis

Related to [[Causal Inference]] and [[Regression Analysis]].
See also [[Statistical Power]].
```

### "Out of memory"

For very large vaults:
```bash
# Limit to core nodes
nexus knowledge vault graph --limit 200 --json > graph.json
```

### "Graph is too dense"

Filter by minimum connections:

```python
# Keep only well-connected nodes
min_connections = 3
filtered_nodes = [n for n in data['nodes'] if n.get('connections', 0) >= min_connections]
```

## Next Steps

- **First Steps**: [Get started with Nexus](first-steps.md)
- **Vault Setup**: [Optimize your vault](vault-setup.md)
- **Writing**: [Use graph insights in writing](../guide/writing.md)

## Resources

- [Network Science Book](http://networksciencebook.com/)
- [D3.js Gallery](https://observablehq.com/@d3/gallery)
- [Gephi Graph Viz](https://gephi.org/)
- [NetworkX Documentation](https://networkx.org/)
