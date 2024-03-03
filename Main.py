
from Graphing import construct_graph, get_difference_graph, find_alternating_cycles, create_cycle_graph, find_edge_swaps, swap_edges
from GraphIO import display_graphs, load_graphs, save_graph
from typing import Callable, TypeVar, Iterable
from itertools import combinations
from random import random
from time import perf_counter_ns
from networkx import empty_graph, Graph, DiGraph, compose, is_valid_degree_sequence_erdos_gallai as is_valid_degree_sequence

def generate_graphs (degrees):
    # Can be removed or changed
    labels = "abcdefghijklmnopqrstuvwxyz"
    # labels = None

    G1 = construct_graph(degrees, nodeLabels=labels)
    G1.graph['name'] = "G1"

    G2 = construct_graph(degrees, nodeLabels=labels)
    G2.graph['name'] = "G2"

    DG = get_difference_graph(G1, G2)

    display_graphs(G1, G2, DG)

    ans = input("Save the graphs?\n>").lower()
    if ans == "y" or ans == "yes":
        name = input("Name of graph: ")
        save_graph(G1, name+"_G1")
        save_graph(G2, name+"_G2")

def attempt_graphs (name:str):
    G1, G2 = load_graphs(name)
    DG = get_difference_graph(G1, G2)
    cycles = find_alternating_cycles(G1, G2)
    CG = create_cycle_graph(cycles[0])
    for u,v,c in DG.edges.data('color'):
        try: CG[u][v]['color'] = c
        except: CG[v][u]['color'] = c
    CG.graph['name'] = "Cycle"
    display_graphs(G1, G2, DG, CG)

def create_degree_sequence (length:int, edgeChance:float=0.5, heavyTailBias:float=0) -> list[int]:
    if __debug__: assert length >= 0
    multDif :float = 1 - heavyTailBias / length
    retr = [0] * length
    for u,v in combinations(range(length), 2):
        if random() < edgeChance:
            retr[u] += 1
            retr[v] += 1
            edgeChance *= multDif
    return retr

def create_difference_graph (length:int) -> Iterable[Graph]:
    g :Graph = empty_graph(length)
    edges = list(combinations(g.nodes, 2))
    return [] # TODO: DO ME

_T = TypeVar("_T")
def timeit (func:Callable[...,_T], *args, **kargs) -> tuple[int, _T]:
    start = perf_counter_ns()
    retr = func(*args, **kargs)
    end = perf_counter_ns()
    return (end-start, retr)

def gather_input (prompt:str, parser:Callable[[str],_T] = lambda x: x) -> _T:
    "Continiously `prompt`s the user for input until the `parser` succeeds, the `parser` should throw an exception if the given input is invalid"
    while True:
        ans = input(prompt)
        try:
            result = parser(ans)
            return result
        except Exception as err:
            print("Invalid input supplied:", err)

def main ():
    method = gather_input(
        "What algorithm would you like to test?\n(1) find_alternating_cycles\n(2) find_edge_swaps\n(3) generate_graphs\n> ",
        lambda ans: int(ans) if ans != "" else 0
    )
    if method == 0: return
    if method == 1 or method == 2:
        ans = gather_input(
            "What type of graph would you like to attempt with?\n(1) Supply a degree sequence\n(2) Create a random degree sequence\n(3) Use a premade graph pair\n> ",
            lambda ans: int(ans) if ans != "" else 0
        )
        G1, G2 = None, None
        if ans == 1:
            def parse_deg_seq (text)->list[int]:
                deg = [int(s) for s in text.split()]
                assert is_valid_degree_sequence(deg), "Invalid degree sequence"
                return deg
            degreeSequence = gather_input(
                "Please supply a degree sequence seperated by whitespace...\n> ", parse_deg_seq
            )
            nodeLabels = "abcdefghijklmnopqrstuvwxyz" if len(degreeSequence) <= 26 else None
            G1 = construct_graph(degreeSequence, nodeLabels=nodeLabels)
            G2 = construct_graph(degreeSequence, nodeLabels=nodeLabels)
        elif ans == 2:
            length = gather_input(
                "Please input length of degree sequence: ",
                lambda ans: (i := int(ans)) and i >= 0 and i
            )
            edgeChance = gather_input(
                "Optionally, input the chance for each edge, (default 0.5): ",
                lambda ans: float(ans) if ans != "" else 0.5
            )
            heavyTailBias = gather_input(
                "Optionally, input a heavy tail bias weight in [0, 1.0], (default 0): ",
                lambda ans: float(ans) if ans != "" else 0.0
            )
            degreeSequence = create_degree_sequence(length, edgeChance, heavyTailBias)
            nodeLabels = "abcdefghijklmnopqrstuvwxyz" if len(degreeSequence) <= 26 else None
            G1 = construct_graph(degreeSequence, nodeLabels=nodeLabels)
            G2 = construct_graph(degreeSequence, nodeLabels=nodeLabels)
        elif ans == 3:
            G1, G2 = gather_input(
                "Please input the name of the graph pair: ",
                lambda ans: load_graphs(ans)
            )
        else:
            return
        G1.graph['name'] = "G1"
        G2.graph['name'] = "G2"
        DG = get_difference_graph(G1, G2)
        if method == 1:
            cycles = find_alternating_cycles(G1, G2)
            CG = empty_graph(DG.nodes, DiGraph)
            for cycle in cycles:
                subCG = create_cycle_graph(cycle)
                CG = compose(CG, subCG)
            for u,v,c in DG.edges.data('color'):
                try: CG[u][v]['color'] = c
                except: CG[v][u]['color'] = c
            display_graphs(G1, G2, DG, CG)
        elif method == 2:
            swaps = find_edge_swaps(G1, G2)
            graphs :list[Graph] = []
            GN = G1.copy()
            for i, swap in enumerate(swaps):
                Gk = GN.copy()
                Gk.graph['name'] = f"G{i+1}"
                Gk.add_edge(*swap[0], color='red', style='dashed')
                Gk.add_edge(*swap[1], color='red', style='dashed')
                Gk.add_edge(swap[0][0], swap[1][0], color='green', style='dashed')
                Gk.add_edge(swap[0][1], swap[1][1], color='green', style='dashed')
                graphs.append(Gk)
                swap_edges(GN, *swap)
            GN.graph['name'] = 'GN'
            graphs.append(GN)
            display_graphs(*graphs, get_difference_graph(G1, G2))



if __name__ == "__main__": main()
