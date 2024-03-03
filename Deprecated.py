
from itertools import combinations_with_replacement
from typing import TypeVar, Hashable
from networkx import Graph, DiGraph, complete_graph, difference, compose, simple_cycles, connected_components, \
    is_valid_degree_sequence_erdos_gallai as is_valid_degree_sequence

NodeType = Hashable

def get_complete_difference_graph (G1:Graph, G2:Graph) -> Graph:
    """Returns a complete graph where every edge is one of the following:
    - red & solid = This edge must be removed
    - green & solid = This edge must be added
    - red & dashed = The edge can be removed, but we dont want to
    - green & dashed = The edge can be added, but we dont want to

    Solid lines are of weight -1, and dashed lines are of weight +1
    """
    differenceGraph :Graph = complete_graph(G1)
    differenceGraph.graph['name'] = "Difference"
    differenceGraph.graph['complete'] = True
    toBeRemoved :Graph = difference(G1, G2)
    toBeInserted :Graph = difference(G2, G1)
    for u,v in toBeRemoved.edges:
        differenceGraph.edges[u,v].update({
            'color': 'red',
            'style': 'solid',
            'weight': -1
        })
    for u,v in toBeInserted.edges:
        differenceGraph.edges[u,v].update({
            'color': 'green',
            'style': 'solid',
            'weight': -1
        })
    for u,v in difference(G1, toBeRemoved).edges:
        differenceGraph.edges[u,v].update({
            'color': 'red',
            'style': 'dashed',
            'weight': +1
        })
    for u,v in difference(differenceGraph, compose(G1, G2)).edges:
        differenceGraph.edges[u,v].update({
            'color': 'green',
            'style': 'dashed',
            'weight':+1
        })
    return differenceGraph

_T = TypeVar('_T')
def get_pairs_from_list (L:list[_T]) -> list[tuple[_T,_T]]:
    """Returns a list of all pairs of items from the given list `L`.

    If (a,b) is a pair, then (b,a) is skipped"""
    return [
        (a, b)
        for i,a in enumerate(L)
        for b in L[i+1:]
    ]

def get_edge_node_graph (DG:Graph) -> DiGraph:
    """This function is entirely overkill, but its here anyways.

    For the given graph `DG`, this function returns a *directed* graph
    where every node is an edge in `DG`, and
    every edge is an edge-to-edge in `DG`
    where they share a node and alternate from green->red or red->green.

    The nodes share the color/weight of the edge it represents,
    and the nodes size is 450 if it's edge is solid, 150 otherwise."""
    key = lambda u,v: (u,v)
    ENG :DiGraph = DiGraph(bipartite=True)
    ENG.add_nodes_from(
        [key(*p) for p in DG.edges] + [key(p[1], p[0]) for p in DG.edges]
    )
    for p in DG.edges:
        colour = DG.edges[p[0],p[1]]['color']
        size = 450 if DG.edges[p[0],p[1]].get('style', 'solid') == 'solid' else 150
        weight = -1 if size == 450 else +1
        ENG.nodes[key(*p)].update({
            'color': colour,
            'size': size,
            'weight': weight
        })
        ENG.nodes[key(p[1],p[0])].update({
            'color': colour,
            'size': size,
            'weight': weight
        })
    for u1,u2 in DG.edges:
        for v1 in DG.neighbors(u1):
            if v1 != u2 and ENG.nodes[key(u2,u1)]['color'] != ENG.nodes[key(u1,v1)]['color']:
                ENG.add_edge(key(u2,u1), key(u1,v1))
        for v2 in DG.neighbors(u2):
            if v2 != u1 and ENG.nodes[key(u1,u2)]['color'] != ENG.nodes[key(u2,v2)]['color']:
                ENG.add_edge(key(u1,u2), key(u2,v2))
    ENG.graph['labels'] = {
        (u,v) : str(u)+","+str(v)
        for u,v in ENG
    }
    return ENG

def get_best_cycles (G:Graph) -> tuple[int, list[list[NodeType]]]:
    """This very brute force function finds all the cycles in an Edge Node graph G, and
    returns the minimum cost and a list of all cycles with that cost.
    Edge-Node meaning each node of `G` must be an edge represented as a pair.
    Returns (`minCost`, `list[cycle]`), where each cycle is a list of Nodes."""
    cycles = [
        [n for n in edgeCycle]
        for edgeCycle in simple_cycles(G)
        if not any(
            (v,u) in edgeCycle
            for u,v in edgeCycle
        )
    ]
    cycleCosts = [
        sum(
            G.nodes[n]['weight']
            for n in nodeCycle
        ) for nodeCycle in cycles
    ]
    minCost = min(cycleCosts)
    return (minCost, [
        [
            u for u,_ in edgeCycle # Discard edge info, just keep nodes
        ] for i, edgeCycle in enumerate(cycles)
        if cycleCosts[i] == minCost
    ])

def find_alternating_cycles_0 (CG:Graph) -> tuple[list[NodeType], ...]:
    components :list[set[NodeType]] = list(connected_components(CG))
    def get_cycle (comp:set[NodeType]) -> list[NodeType]:
        startNode, _ = max(CG.degree(comp), key=lambda t: t[1])
        cycle :list[NodeType] = [ startNode ]
        curColor :str = ""
        # Explore all connected nodes in a single path until cycle found
        while True:
            # Explore all neighbors
            nextNode :NodeType = None
            for n2 in CG.neighbors(cycle[-1]):
                edge = CG[cycle[-1]][n2]
                if edge.get('visited',False):
                    continue
                if (c := edge['color']) != curColor:
                    nextNode = n2
                    curColor = c
                    break
            if nextNode is None:
                return cycle
            CG[cycle[-1]][nextNode]['visited'] = True
            cycle.append(nextNode)
    return tuple(
        get_cycle(c) for c in components if len(c) >= 4
    )

def combine_alternating_cycles (G:Graph, cycles :list[list[NodeType]]) -> list[NodeType]:
    "Assumes the first cycle is the parent and the rest touch the parent at index 0, this function combines them into one alternating cycle"
    if len(cycles) == 0:
        return []
    parent = cycles[0]
    for subCycle in cycles[1:]:
        centre = subCycle[0]
        i = parent.index(centre)
        entryColourSub = G[subCycle[-1]][centre]['color']
        exitColourSub = G[centre][subCycle[1]]['color']
        entryColourParent = G[parent[i-1]][centre]['color']
        exitColourParent = G[centre][parent[(i+1)%len(parent)]]['color']
        if entryColourParent != exitColourSub:
            assert entryColourSub != exitColourParent
            parent = parent[:i] + subCycle + parent[i:]
        else:
            assert entryColourParent != entryColourSub
            assert exitColourParent != exitColourSub
            parent = parent[:i+1] + list(reversed(subCycle)) + parent[i+1:]
    return parent

def generate_degree_sequences(upToLength:int, startFrom:int=2):
    with open("DegreeSequences.txt", 'w') as fout:
        fout.writelines(
            ",".join(str(i) for i in seq)+"\n"
            for L in range(startFrom, upToLength+1)
            for seq in combinations_with_replacement(range(L-1,0,-1), L)
            if sum(seq) % 2 == 0
            if is_valid_degree_sequence(seq)
        )