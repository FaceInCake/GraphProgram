
from typing import Hashable, Sequence, Iterable
from random import randint
from itertools import pairwise
from networkx import Graph, DiGraph, empty_graph, difference

NodeType = Hashable
EdgeType = tuple[NodeType, NodeType]


def construct_graph (degreeSequence:Sequence[int], *, nodeLabels:Sequence[NodeType]|None=None) -> Graph:
    "Implements the Havel-Hakimi algorithm for generating a random graph of the given degree sequence"
    if nodeLabels is not None:
          _nodeLabels :list[NodeType] = list(nodeLabels[:len(degreeSequence)])
    else: _nodeLabels :list[NodeType] = [i for i in range(len(degreeSequence))]
    # random.shuffle(_nodeLabels)
    if len(_nodeLabels) < len(degreeSequence):
        raise ValueError("nodeLabels must be of equal or greater length than degreeSequence")
    nodeDegrees :list[tuple[NodeType,int]] = sorted(zip(
        _nodeLabels, list(degreeSequence[:])
    ), key=lambda x:x[1], reverse=True) # Copy list and sort it
    G :Graph = empty_graph(_nodeLabels)
    for _ in range(len(nodeDegrees)):
        k = randint(0, len(nodeDegrees)-1)
        kIndex, kDegrees = nodeDegrees.pop(k)
        if kDegrees > len(nodeDegrees):
            raise ValueError("Degree sequence forms an invalid graph: "+str(degreeSequence))
        for i in range(kDegrees):
            if nodeDegrees[i][1] <= 0:
                raise ValueError("Degree sequence forms an invalid graph: "+str(degreeSequence))
            G.add_edge(kIndex, nodeDegrees[i][0])
            nodeDegrees[i] = (nodeDegrees[i][0], nodeDegrees[i][1] - 1)
        nodeDegrees.sort(key=lambda x:x[1], reverse=True)
    return G

def create_cycle_graph (cycle:list[NodeType]) -> DiGraph:
    CG :DiGraph = empty_graph(cycle, DiGraph)
    if len(cycle)==0: return CG
    for i, (u,v) in enumerate(pairwise(cycle + [cycle[0]])):
        CG.add_edge(u, v, label=(i+1))
    return CG

def get_difference_graph (G1:Graph, G2:Graph) -> Graph:
    """Returns a graph where every edge has a 'color' attribute where:
    
    red : That edge is in G1 but not G2
    
    green : That edge is in G2 but not G1
    
    There is always a cycle in this graph if G1 and G2 have the same degree sequence"""
    DG :Graph = empty_graph(G1.nodes)
    DG.graph['name'] = "Difference"
    toBeRemoved :Graph = difference(G1, G2)
    for u,v in toBeRemoved.edges:
        DG.add_edge(u, v, color='red')
    toBeInserted :Graph = difference(G2, G1)
    for u,v in toBeInserted.edges:
        DG.add_edge(u, v, color='green')
    return DG

def get_components (G:Graph) -> Iterable[list[NodeType]]:
    """Returns a generator that yields lists of nodes, or more generally, the components of the given graph.
    Generator returns number of components yielded when iteration stops."""
    notVisited :set = set(G.nodes)
    componentCount :int = 0
    for _n in G.nodes:
        if _n in notVisited:
            component :list[NodeType] = [ _n ]
            notVisited.remove(_n)
            for n1 in component:
                for n2 in G.neighbors(n1):
                    if n2 in notVisited:
                        component.append(n2)
                        notVisited.remove(n2)
            yield component
            componentCount += 1
            if len(notVisited)==0: return

def find_alternating_cycles (G1:Graph, G2:Graph) -> list[list[NodeType]]:
    "Returns a list of alternating cycles, always starting from an edge *to be added*"
    cycles :list[list[NodeType]] = []
    toAdd :Graph = difference(G2, G1)
    toRemove :Graph = difference(G1, G2)
    nodes = list(G1.nodes)
    while nodes and (start := nodes.pop()):
        cycle :list[NodeType] = [ start ]
        colour :Graph = True
        curGraph = toAdd
        while candidates := [
            n for n in curGraph.neighbors(cycle[-1])
        ]:
            curGraph.remove_edge(cycle[-1], candidates[0])
            cycle.append(candidates[0])
            if candidates[0] in nodes: nodes.remove(candidates[0])
            curGraph = toRemove if colour else toAdd
            colour = not colour
        if len(cycle) > 1: cycles.append(cycle[:-1])
    return cycles

def swap_edges (G:Graph, edge1:EdgeType, edge2:EdgeType):
    G.remove_edge(edge1[0], edge1[1])
    G.remove_edge(edge2[0], edge2[1])
    G.add_edge(edge1[0], edge2[0])
    G.add_edge(edge1[1], edge2[1])

def find_edge_swaps (_G1:Graph, G2:Graph) -> list[tuple[EdgeType,EdgeType]]:
    G1 = _G1.copy()
    DG = get_difference_graph(G1, G2)

    def find_valid_nodes(edges:list[NodeType,NodeType,str]) -> tuple[EdgeType, EdgeType, str, str]:
        for e2, e3, c23 in edges:
            DG.remove_edge(e2, e3)
            for e1 in list(DG.neighbors(e2)):
                if DG[e2][e1]['color'] == c23: continue
                for e4 in DG.neighbors(e3):
                    if e4 != e1 \
                    and DG[e2][e1]['color'] == DG[e3][e4]['color'] \
                    and (
                        not DG.has_edge(e1, e4)
                        or DG[e1][e4]['color'] == c23
                    ):
                        return e1, e2, e3, e4, c23
            DG.add_edge(e2, e3, color=c23)
        raise RuntimeError("Unable to find a valid swap, even though one should always exist")

    def find_valid_swap ():
        edges = list(DG.edges.data('color'))
        if len(edges) == 0: return []
        E1, E2, E3, E4, C23 = find_valid_nodes(edges)
        DG.remove_edge(E1, E2)
        DG.remove_edge(E3, E4)
        if DG.has_edge(E1, E4):
            DG.remove_edge(E1, E4)
            edgeSwap = ((E1,E2), (E4,E3)) if C23 == 'green' else ((E2,E3), (E1,E4))
            swap_edges(G1, *edgeSwap)
            return [edgeSwap] + find_valid_swap()
        else:
            if C23 == 'green':
                DG.add_edge(E1, E4, color='red')
                edgeSwap = ((E1,E2), (E4,E3))
                if not G1.has_edge(E1, E4):
                    swap_edges(G1, *edgeSwap)
                    return [edgeSwap] + find_valid_swap()
                return find_valid_swap() + [edgeSwap]
            else: # red
                DG.add_edge(E1, E4, color='green')
                edgeSwap = ((E2,E3), (E1,E4))
                if G1.has_edge(E1, E4):
                    swap_edges(G1, *edgeSwap)
                    return [edgeSwap] + find_valid_swap()
                return find_valid_swap() + [edgeSwap]

    return find_valid_swap()
