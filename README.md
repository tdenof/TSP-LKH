# TSP-LKH
Solve the travel salesman problem using Lin Keringham algorithm.

The code is originally taken from Marlboro's College Python programming course.
http://cs.marlboro.edu/courses/fall2012/python/notes/Nov_27.attachments/traveling_salesman

The core part of path search is the same, but code arragement was reworked.
The custom svg_graph drawing method is replaced by matplotlib.
The classes were separated on multiple files.
The input data can be given as a CSV file.
The algorithm parameters can be given now as command line arguments.

usage: tsp.py [-h] [-n NEIGHBORS] [-f FILE] [-d DEPTH] [-v]

Lin Keringhan Algorithm.

optional arguments:
  -h, --help            show this help message and exit
  -n NEIGHBORS, --neighbors NEIGHBORS
                        Neighbors count to test for new roads, default 3.
  -f FILE, --file FILE  Dataset input file in csv format, if not given will
                        look for the file 'dataset.csv'.
  -d DEPTH, --depth DEPTH
                        Depth of search, if given transform the algorithm into
                        a fixed lambda-opt search.
  -v, --verbose         Print detailed information about road search.

