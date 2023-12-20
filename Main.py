
from Graphing import construct_graph, get_difference_graph, find_alternating_cycles
from GraphIO import display_graphs, load_graphs, save_graph
from typing import Callable, TypeVar
from itertools import combinations_with_replacement
from time import perf_counter_ns
from networkx import is_valid_degree_sequence_erdos_gallai as is_valid_degree_sequence

def generate_graphs ():
    # Can be removed or changed
    labels = "abcdefghijklmnopqrstuvwxyz"

    # degrees = [3, 2, 2, 2, 1]
    # degrees = [4, 1, 2, 3, 1, 3]
    # degrees = [5, 2, 2, 3, 3, 2, 3]
    # degrees = [2, 2, 2, 2, 2, 2, 1, 1]
    # degrees = [2, 2, 2, 3, 3, 3, 3]
    degrees = [6, 2, 4, 3, 3, 2, 3, 1, 2]

    G1 = construct_graph(degrees, nodeLabels=labels)
    G1.graph['name'] = "G1"

    G2 = construct_graph(degrees, nodeLabels=labels)
    G2.graph['name'] = "G2"

    DG = get_difference_graph(G1, G2)
    # cycles = find_alternating_cycles(G1, G2)

    # for c in cycles: print(c)

    display_graphs(G1, G2, DG)

    ans = input("Save the graphs?\n>").lower()
    if ans == "y" or ans == "yes":
        name = input("Name of graph: ")
        save_graph(G1, name+"_G1")
        save_graph(G2, name+"_G2")

def attempt_graphs ():
    G1, G2 = load_graphs("Same")

    DG = get_difference_graph(G1, G2)

    cycles = find_alternating_cycles(G1, G2)

    for cycle in cycles:
        print(cycle)

    display_graphs(G1, G2, DG)

def generate_degree_sequences(upToLength:int, startFrom:int=2):
    with open("DegreeSequences.txt", 'w') as fout:
        fout.writelines(
            ",".join(str(i) for i in seq)+"\n"
            for L in range(startFrom, upToLength+1)
            for seq in combinations_with_replacement(range(L-1,0,-1), L)
            if sum(seq) % 2 == 0
            if is_valid_degree_sequence(seq)
        )

_T = TypeVar("_T")
def timeit (func:Callable[...,_T], *args, **kargs) -> tuple[int, _T]:
    start = perf_counter_ns()
    retr = func(*args, **kargs)
    end = perf_counter_ns()
    return (end-start, retr)

def main ():
    # generate_graphs()
    # attempt_graphs()
    # generate_degree_sequences(12, 11)
    pass
    

if __name__ == "__main__": main()