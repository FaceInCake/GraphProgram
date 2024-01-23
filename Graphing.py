
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

def traverse_alternating_cycle (_AG :Graph, _start :NodeType) -> list[list[NodeType]]:
    AG = _AG.copy()
    subCycles :list[list[NodeType]] = []
    cycleStarts :list[NodeType] = [ _start ]
    # Find all connected nodes, break when no more open edges
    for start in cycleStarts:
        cycle :list[NodeType] = [ start ]
        curColor :str = ""
        # Explore all connected nodes in a single path until cycle found
        while len(candidates := [
            n for n in AG.neighbors(cycle[-1])
            if  AG.has_edge(cycle[-1], n)
            and AG[cycle[-1]][n].get('color','black') != curColor
        ]) != 0:
            if len(candidates) > 1:
                cycleStarts.append(cycle[-1])
            curColor = AG[cycle[-1]][candidates[0]].get('color','black')
            AG.remove_edge(cycle[-1], candidates[0])
            cycle.append(candidates[0])
        if len(cycle) > 1: subCycles.append(cycle[:-1])
    return subCycles

def find_alternating_cycles (G1:Graph, G2:Graph) -> list[list[NodeType]]:
    DG = get_difference_graph(G1, G2)
    components = list(get_components(DG))
    return [
        combine_alternating_cycles(DG,
            traverse_alternating_cycle(DG, next(iter(c)))
        )
        for c in components
    ]
