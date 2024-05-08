
## GraphIO
Contains several functions for input and output of graph objects.
There's a convenience save and load function, which just uses `gexf`.

There's also a `display_graphs` function which can take a number of graphs
and use the graphs' attributes for modifying the displayed graph, like 'color'.

## Deprecated
Contains no longer used code that is kept for archiving purposes

## Graphing
Contains several functions for applying higher level filtering or parsing of graph objects.

## Main
Can be run from an interactive terminal for executing different code snippets.

## test_main
Contains all test cases and testing functionality.

## TestGraphs
Contains a number of graph pairs to test with.
For each graph pair there are three files:
(*name*)_G1.gexf, (*name*)_G2.gexf, and (*name*).png.
The two gexf files are XML type files for storing the two graphs.
They can be viewed and edited with any text editor.
There is also the PNG, which is a figure of both graphs and the difference graph, of ease of viewing.

# Dependencies
- NetworkX: `pip install networkx`
- MatPlotLib: `pip install matplotlib`
- (If using a virtual environment)
  - PyTest: `pip install pytest`
