
import unittest
from typing import Iterable
from collections import defaultdict
from itertools import pairwise, chain
from GraphIO import load_graphs
from Graphing import NodeType, construct_graph, get_difference_graph, get_components, \
    find_alternating_cycles, swap_edges, find_edge_swaps
from Deprecated import traverse_alternating_graph
import networkx as nx


class Test_construct_graph (unittest.TestCase):

    def standard_test (self, msg, degreeSequence:list[int], nodeLabels:list|None=None):
        G = construct_graph(degreeSequence, nodeLabels=nodeLabels)
        self.assertIsNotNone(G, msg)
        self.assertEqual(
            G.number_of_nodes(), len(degreeSequence),
            "Number of nodes of graph should match length of degree sequence"
        )
        # Create map of: degree -> count of degree in sequence
        degMap = defaultdict(lambda: 0)
        for i in degreeSequence: degMap[i] += 1
        # Check that the count of degrees match
        # (This is because the degrees of G could be in any order compared to the one given)
        GD = list(dict(G.degree).values())
        for deg, count in degMap.items():
            self.assertEqual(
                count, GD.count(deg),
                "Degree sequence of graph doesnt match the one given"
            )
        if nodeLabels is not None:
            expectedLabels = nodeLabels[:len(degreeSequence)]
            for n in G.nodes(False):
                self.assertIn(n, expectedLabels,
                    "Expected given node label to exist in graph, but it doesnt"
                ) 

    def test_simple (self):
        self.standard_test(
            "Simple graph of deg.seq [2,1,1] should be valid",
            [1, 2, 1]
        )

    def test_length5 (self):
        self.standard_test(
            "Valid degree sequence should return a valid graph",
            [3, 2, 2, 2, 1]
        )

    def test_sparse (self):
        self.standard_test(
            "Graph of even length where all nodes have 1 edge should be valid",
            [1, 1, 1, 1]
        )

    def test_complete10 (self):
        self.standard_test(
            "Complete graph with 10 nodes should be valid",
            [9, 9, 9, 9, 9, 9, 9, 9, 9, 9]
        )

    def test_invalid_short (self):
        with self.assertRaises(ValueError,
        msg="Graph with 1 edge but one node is invalid and should error"):
            _ = construct_graph([1])

    def test_invalid_sparse (self):
        with self.assertRaises(ValueError,
        msg="Graph of odd length where all nodes only have 1 edge is invalid and should error"):
            _ = construct_graph([1, 1, 1, 1, 1, 1, 1])

    def test_weird_degree_order (self):
        self.standard_test(
            "Degree should be able to be in any order",
            [2, 3, 2, 1, 2]
        )

    def test_with_labels (self):
        self.standard_test(
            "Providing 3 node labels for a graph with 3 nodes should be valid",
            [1, 2, 1],
            ["apple", "banana", "orange"]
        )

    def test_not_enough_labels (self):
        with self.assertRaises(ValueError,
        msg="Providing fewer node labels than node count should error"):
            _ = construct_graph([1, 1, 2],
                nodeLabels=["hello"]
            )

    def test_many_labels (self):
        self.standard_test(
            "Having more labels than nodes should be valid",
            [1, 2, 2, 2, 3],
            "abcdefghijklmnopqrstuvwxyz"
        )

class Test_get_components (unittest.TestCase):

    def standard_test (self, G:nx.Graph, expected:list[set[NodeType]]):
        actual = [set(c) for c in get_components(G)]
        self.assertEqual(len(expected), len(actual),
            f"Expected '{len(expected)}' components but found '{len(actual)}'")
        for expC in reversed(expected):
            for actC in reversed(actual):
                if len(expC) == len(actC):
                    if expC == actC:
                        actual.remove(actC)
                        expected.remove(actC)
                        break
        self.assertEqual(0, len(expected), f"Failed to find component(s): '{expected}'")
        self.assertEqual(0, len(actual), f"Unexpected extra component(s): '{actual}'")

    def test_path (self): self.standard_test(nx.path_graph(5), [set(range(5))])

    def test_cycle (self): self.standard_test(nx.cycle_graph(4), [set(range(4))])

    def test_two_paths (self):
        G = nx.path_graph(10)
        nx.add_path(G, range(11,21))
        self.standard_test(G, [set(range(10)), set(range(11,21))])
    
    def test_complete (self): self.standard_test(nx.complete_graph(100), [set(range(100))])

    def test_empty (self): self.standard_test(nx.empty_graph(5), [set([i]) for i in range(5)])

    def test_null (self): self.standard_test(nx.null_graph(), [])

    def test_ladder (self): self.standard_test(nx.ladder_graph(20), [set(range(40))])

    def test_trivial (self): self.standard_test(nx.trivial_graph(), [set([0])])

    def test_mixed (self):
        G :nx.Graph = nx.cycle_graph(6)
        nx.add_star(G, range(6, 16))
        nx.add_path(G, range(16, 20))
        G = nx.compose(G, nx.complete_graph(range(20,25)))
        self.standard_test(G, [
            set(range(6)), set(range(6,16)), set(range(16,20)), set(range(20,25))
        ])

class Test_traverse_alternating_cycle (unittest.TestCase):

    def standard_test (self, name:str, expected:Iterable[NodeType]):
        G1, G2 = load_graphs(name)
        ExpG :nx.Graph = nx.cycle_graph(expected)
        CG = get_difference_graph(G1, G2)
        for i, start in enumerate(expected):
            with self.subTest(i=i, start=start):
                EG = ExpG.copy()
                cycles = traverse_alternating_graph(CG, start)
                for cycle in cycles:
                    for u,v in pairwise(cycle+[cycle[0]]):
                        EG.remove_edge(u, v)
                    for (u1,v1), (_,v2) in pairwise(pairwise(cycle+cycle[:2])):
                        self.assertNotEqual(
                            (c := CG[u1][v1]['color']),
                            CG[v1][v2]['color'],
                            f"Two adjoining edges have the same colour '{c}' when they shouldn't"
                        )
                self.assertEqual(EG.number_of_edges(), 0, "There were some edges expected that werent found")

    def test_square (self): self.standard_test("Square", list("bced"))

    def test_hourglass (self): self.standard_test("Hourglass", list("eacbdc"))

    def test_figureeight (self): self.standard_test("FigureEight", list("feadcbgd"))

    def test_same (self): self.standard_test("Same", [])

    def test_hexagon (self): self.standard_test("Hexagon", list("abfcde"))

    def test_crown (self): self.standard_test("Crown", list("dfgacdeg"))

    def test_ears (self): self.standard_test("Ears", list("decdgbafgefb"))

    def test_pineapple (self): self.standard_test("Pineapple", list("abchfgaefd"))

    def test_threesquares (self): self.standard_test("ThreeSquares", list("abfehgacde"))

    def test_web (self): self.standard_test("Web", list("abcegadebgdc"))

    def test_bird (self): self.standard_test("Bird", list("ibhaecdgcabc"))

    def test_twocomponents (self):
        self.standard_test("TwoComponents", list("bfcg"))
        self.standard_test("TwoComponents", list("deia"))

class Test_find_alternating_cycles (unittest.TestCase):

    def standard_test (self, G1:nx.Graph, G2:nx.Graph, expected:list[list[NodeType]]):
        EG = nx.Graph()
        for e in expected:
            nx.add_cycle(EG, e)
        actual = find_alternating_cycles(G1, G2)
        self.assertEqual(len(expected), len(actual),
            "Unexpected number of cycles")
        AG :nx.Graph = nx.empty_graph(list(chain(*actual)))
        # Duplicate edge entries are simply ignored when creating a graph, but we wanna catch and fail if found
        edges = set()
        for actualCycle in actual:
            for actualEdge in pairwise(actualCycle + [actualCycle[0]]):
                self.assertNotIn(actualEdge, edges,
                    f"Unexpected duplicate edge: '{actualEdge}'"
                )
                edges.add(actualEdge)
        AG.add_edges_from(edges)
        self.assertEqual(EG.nodes, AG.nodes)
        self.assertEqual(EG.edges, AG.edges)

    def test_twocomponents (self):
        G1, G2 = load_graphs("TwoComponents")
        self.standard_test(G1, G2, [list("bfcg"), list("deia")])

    def test_same (self):
        G1, G2 = load_graphs("Same")
        self.standard_test(G1, G2, [])

    def test_null (self):
        G1 = nx.null_graph()
        G2 = nx.null_graph()
        self.standard_test(G1, G2, [])

    def test_trivial (self):
        G1 = nx.trivial_graph()
        G2 = nx.trivial_graph()
        self.standard_test(G1, G2, [])

    def test_empty (self):
        G1 = nx.empty_graph(100)
        G2 = nx.empty_graph(100)
        self.standard_test(G1, G2, [])

    def test_hexagon (self):
        G1, G2 = load_graphs("Hexagon")
        self.standard_test(G1, G2, [list("abfcde")])

    def test_square (self):
        G1, G2 = load_graphs("Square")
        self.standard_test(G1, G2, [list("bced")])

class Test_find_edge_swaps (unittest.TestCase):

    def standard_test (self, G1:nx.Graph, G2:nx.Graph):
        swaps = find_edge_swaps(G1, G2)
        for i, (e1, e2) in enumerate(swaps):
            with self.subTest(i=i, swapA=e1, swapB=e2):
                self.assertNotEqual(e1[0], e1[1], "Invalid edge swap")
                self.assertNotEqual(e2[0], e2[1], "Invalid edge swap")
                self.assertNotEqual(e1[0], e2[0], "Invalid edge swap")
                self.assertNotEqual(e1[1], e2[1], "Invalid edge swap")
                self.assertTrue(G1.has_edge(*e1), "source graph does not contain edge 1 when it should")
                self.assertTrue(G1.has_edge(*e2), "source graph does not contain edge 2 when it should")
                self.assertFalse(G1.has_edge(e1[0], e2[0]), "source graph contains edge e11-e21 when it shouldNT")
                self.assertFalse(G1.has_edge(e1[1], e2[1]), "source graph contains edge e12-e22 when it shouldNT")
                swap_edges(G1, e1, e2)
        with self.subTest('FinalCheck'):
            self.assertEqual(G1.edges, G2.edges, "After applying the edge swaps, G1 and G2 should now be the same, but they werent")

    def test_square (self):
        G1, G2 = load_graphs("Square")
        self.standard_test(G1, G2)
    def test_same (self):
        G1, G2 = load_graphs("Same")
        self.standard_test(G1, G2)
    def test_hourlgass (self):
        G1, G2 = load_graphs("Hourglass")
        self.standard_test(G1, G2)
    def test_hexagon (self):
        G1, G2 = load_graphs("Hexagon")
        self.standard_test(G1, G2)
    def test_figureeight (self):
        G1, G2 = load_graphs("FigureEight")
        self.standard_test(G1, G2)
    def test_ears (self):
        G1, G2 = load_graphs("Ears")
        self.standard_test(G1, G2)
    def test_crown (self):
        G1, G2 = load_graphs("Crown")
        self.standard_test(G1, G2)
    def test_bird (self):
        G1, G2 = load_graphs("Bird")
        self.standard_test(G1, G2)
    def test_pineapple (self):
        G1, G2 = load_graphs("Pineapple")
        self.standard_test(G1, G2)
    def test_three_squares (self):
        G1, G2 = load_graphs("ThreeSquares")
        self.standard_test(G1, G2)
    def test_two_components (self):
        G1, G2 = load_graphs("TwoComponents")
        self.standard_test(G1, G2)
    def test_web (self):
        G1, G2 = load_graphs("Web")
        self.standard_test(G1, G2)
    def test_size12 (self):
        G1, G2 = load_graphs("Size12")
        self.standard_test(G1, G2)
    def test_len26_dense (self):
        G1, G2 = load_graphs("Len26Dense")
        self.standard_test(G1, G2)
    def test_len26_sparse (self):
        G1, G2 = load_graphs("Len26Sparse")
        self.standard_test(G1, G2)
    def test_len26_medium (self):
        G1, G2 = load_graphs("Len26Medium")
        self.standard_test(G1, G2)
    def test_len26_heavytail (self):
        G1, G2 = load_graphs("Len26HeavyTail")
        self.standard_test(G1, G2)


    # def test_all_premade_graphs (self):
    #     graphs = [fn[11:-4] for fn in glob("TestGraphs/*.png")]
    #     for graph in graphs:
    #         with self.subTest(graph=graph):
    #             G1, G2 = load_graphs(graph)
    #             self.standard_test(G1, G2)


if __name__ == "__main__":
    unittest.main()
