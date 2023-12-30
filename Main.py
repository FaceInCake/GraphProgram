
from Graphing import construct_graph, get_difference_graph, find_alternating_cycles, create_cycle_graph
from GraphIO import display_graphs, load_graphs, save_graph
from typing import Callable, TypeVar
from itertools import combinations_with_replacement, combinations
from random import random
from time import perf_counter_ns
from networkx import empty_graph, DiGraph, compose, is_valid_degree_sequence_erdos_gallai as is_valid_degree_sequence

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

def generate_degree_sequences(upToLength:int, startFrom:int=2):
    with open("DegreeSequences.txt", 'w') as fout:
        fout.writelines(
            ",".join(str(i) for i in seq)+"\n"
            for L in range(startFrom, upToLength+1)
            for seq in combinations_with_replacement(range(L-1,0,-1), L)
            if sum(seq) % 2 == 0
            if is_valid_degree_sequence(seq)
        )

def create_degree_sequence (length:int, edgeChance:float=0.5, heavyTailBias:float=0) -> list[int]:
    assert length >= 0
    multDif :float = 1 - heavyTailBias / length
    retr = [0] * length
    for u,v in combinations(range(length), 2):
        if random() < edgeChance:
            retr[u] += 1
            retr[v] += 1
            edgeChance *= multDif
    return retr

_T = TypeVar("_T")
def timeit (func:Callable[...,_T], *args, **kargs) -> tuple[int, _T]:
    start = perf_counter_ns()
    retr = func(*args, **kargs)
    end = perf_counter_ns()
    return (end-start, retr)

def gather_input (prompt:str, parser:Callable[[str],_T] = lambda x: x) -> _T:
    "Continiously prompts the user for input until the parser succeeds, the parser should throw an exception if the given input is invalid"
    while True:
        ans = input(prompt)
        try:
            result = parser(ans)
            return result
        except Exception as err:
            print("Invalid input supplied:", err)

def main ():
    ans = gather_input(
        "Which type of attempt would you like to try?\n(1) Supply a degree sequence\n(2) Create a random degree sequence\n(3) Use a premade graph pair\n> ",
        lambda ans: int(ans) if ans != "" else 0
    )
    G1, G2 = None, None
    if ans == 1:
        degreeSequence = gather_input(
            "Please supply a degree sequence seperated by whitespace...\n> ",
            lambda ans: (deg := [int(s) for s in ans.split()]) and is_valid_degree_sequence(deg) and deg
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
    cycles = find_alternating_cycles(G1, G2)
    CG = empty_graph(DG.nodes, DiGraph)
    for cycle in cycles:
        subCG = create_cycle_graph(cycle)
        CG = compose(CG, subCG)
    for u,v,c in DG.edges.data('color'):
        try: CG[u][v]['color'] = c
        except: CG[v][u]['color'] = c
    display_graphs(G1, G2, DG, CG)

if __name__ == "__main__": main()