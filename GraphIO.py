
from itertools import chain
import matplotlib.pyplot as plt
from networkx import Graph, circular_layout, bipartite_layout, spring_layout, draw as draw_graph, read_gexf, write_gexf


def display_graphs (*graphs:Graph, labels:list[str]|None=None):
    """This function is designed to allow you to just pass in graphs, and it will do the formatting for you.
    However there are some attributes it looks for when you're trying to stylize your graph.
    - node['color'] : changes the color of the node (default lightgrey)
    - node['size'] : changes the size of the node (default 300)
    - edge['color'] : changes the colour of the edge (default black)
    - edge['style'] : changes the type of line: solid/dashed/... (default solid)
    - graph['name'] : Title of the graph when displayed
    - graph['labels'] : dictionary of [node] -> str, to change the labels of the nodes
    - graph['complete'] : If true, the graph is rendered in a circular layout
    - graph['bipartite'] :If true, the graph is rendered in a bipartite layout
    """
    # Lists of lists of data, used: [graphIndex] -> list
    nodeColours = [[c for _,c   in graphs[i].nodes.data('color', default='lightgrey')] for i in range(len(graphs))]
    nodeSizes =   [[s for _,s   in graphs[i].nodes.data('size',  default=300)]         for i in range(len(graphs))]
    edgeColours = [[c for _,_,c in graphs[i].edges.data('color', default='black')]     for i in range(len(graphs))]
    edgeStyles =  [[s for _,_,s in graphs[i].edges.data('style', default='solid')]     for i in range(len(graphs))]
    def get_layout (i):
        if graphs[i].graph.get('complete', False):
            return circular_layout(graphs[i])
        if graphs[i].graph.get('bipartite', False):
            firstColour = list(graphs[i].nodes(data='color'))[0][1]
            if firstColour != None:
                halfNodes = [n for n,c in graphs[i].nodes(data='color') if c == firstColour]
                return bipartite_layout(graphs[i], halfNodes, align='horizontal')
        return spring_layout(graphs[i])
    LEN_TO_GRID :dict[int,tuple[int,int]] = {
        1:(1,1), 2:(1,2), 3:(1,3), 4:(2,2),
        5:(2,3), 6:(2,3), 7:(2,4), 8:(2,4)
    }
    rows, cols = LEN_TO_GRID[len(graphs)]
    _, axes = plt.subplots(nrows=rows, ncols=cols)
    if rows == 1 and cols == 1:
        axes = [axes]
    elif rows > 1 and cols > 1:
        axes = [i for i in chain(*axes)]
    for i in range(len(graphs)):
        draw_graph(
            graphs[i], pos=get_layout(i), ax=axes[i], with_labels=True,
            node_color=nodeColours[i], node_size=nodeSizes[i], labels=graphs[i].graph.get('labels',None),
            edge_color=edgeColours[i], style=edgeStyles[i], font_weight='bold'
        )
        if (graphName := graphs[i].graph.get('name', '')) != "":
            axes[i].set_title(graphName)
    if labels is not None:
        for i in range(len(graphs)):
            axes[i].set_title(labels[i])
    plt.tight_layout()
    plt.axis("off")
    plt.show()

def load_graphs (name:str="Example") -> tuple[Graph, Graph]:
    return (
        read_gexf(f"TestGraphs/{name}_G1.gexf"),
        read_gexf(f"TestGraphs/{name}_G2.gexf")
    )

def save_graph (G:Graph, name:str) -> str:
    s :str = f"TestGraphs/{name}.gexf"
    write_gexf(G, s)
    return s
