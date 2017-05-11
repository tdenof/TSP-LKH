import csv
import random
import argparse
import time
from city import City
from tour import Tour


def tour_improve(tour, lk_max_search_roads, lk_verbose=False, lk_depth_limit=None):

    """ loop over roads ; convert tour to path
        and then start Lin-Kernighan-ish algorithm. """
    (best_length, best_cities) = (tour.tour_length(), tour.city_sequence())

    loop_roads = set(tour)  # loop over a duplicate; tour will be modified.
    print "===== starting tour_improve with %i paths to check" % (2 * len(loop_roads))
    i = 0
    best_iteration = 0
    for road in loop_roads:
        for backward in (True, False):
            i += 1
            tour.revert()
            tour.tour2path(road, backward)
            print "---- calling %i path_search on %s " % (i, str(tour))
            tour2 = path_search(tour, [], [], lk_max_search_roads, lk_verbose, lk_depth_limit)
            print "---- done path_search; found length=%f" % tour2.tour_length()
            if tour2.tour_length() < best_length:
                best_length = tour2.tour_length()
                best_cities = tour2.city_sequence()
                best_iteration = i
            best_tour = Tour(best_cities)
            best_tour.plot_paths(i, best_iteration)
    print "===== finished tour_improve; best is %s " % str(best_tour)
    return best_tour, best_iteration


def path_search(path, added, deleted, lk_max_search_roads, lk_verbose=False, lk_depth_limit=None):
    """ Recursive part of search for an improved TSP solution. """
    depth = len(added)  # also = len(deleted)
    (old_tour_length, old_cities) = (path.tour_length(), path.city_sequence())
    results = [(old_tour_length, old_cities)]
    mods = path.find_lk_mods(lk_max_search_roads, added, deleted)

    if lk_verbose:
        print " " * depth + "  -- path_search " + \
              " depth=%i, path=%f, tour=%f, n_mods=%i " % \
              (depth, path.length, old_tour_length, len(mods))

    for (city, road_add, road_rm) in mods:

        if lk_verbose:
            print " " * depth + "  -> (city, road_add, road_rm) = (%s, %s, %s) " % \
                                (str(city), str(road_add), str(road_rm))

        path.modify(city, road_add, road_rm)

        if lk_verbose:
            print " " * depth + "  -> modified path %s " % str(path)

        added.append(road_add)
        deleted.append(road_rm)

        if lk_depth_limit and depth > lk_depth_limit:
            result_path = path
        else:
            result_path = path_search(path, list(added), list(deleted), lk_max_search_roads, lk_verbose, lk_depth_limit)
        results.append((result_path.tour_length(), result_path.city_sequence()))

        if lk_verbose:
            print " " * depth + "  -> result path=%f; tour=%f" % \
                                (result_path.length, result_path.tour_length())

        added.pop()
        deleted.pop()

        path.unmodify(city, road_add, road_rm)

    # Finished breadth search at this depth ; return best result
    (best_length, best_city_seq) = min(results)
    return Tour(best_city_seq)

parser = argparse.ArgumentParser(description='Lin Kernighan Algorithm.')
parser.add_argument('-n', '--neighbors', type=int, default='3',
                    help='Neighbors count to test for new roads, default 3.')
parser.add_argument('-f', '--file', default='dataset.csv',
                    help='Dataset input file in csv format, if not given will look for the file \'dataset.csv\'.')
parser.add_argument('-d', '--depth', type=int, default=None,
                    help='Depth of search, if given transform the algorithm into a fixed lambda-opt search.')
parser.add_argument('-v', '--verbose', action='store_true',
                    help='Print detailed information about road search.')
args = parser.parse_args()
cmdopt = vars(args)
neighbors = cmdopt.get('neighbors')
dsfile = cmdopt.get('file')
depth = cmdopt.get('depth')
verbose = cmdopt.get('verbose')

cities = []
with open(dsfile) as datasetFile:
    dataset = csv.reader(datasetFile, delimiter=',')
    for row in dataset:
        cities.append(City(row[0], int(row[1]), int(row[2])))
random.shuffle(cities)
Tour.init_roads(cities)
tour = Tour(cities)
answer = 'Y'
while answer in ['Yes', 'yes', 'YES', 'y', 'Y']:
    tour.plot_cities()
    begin = time.time()
    tour, iteration = tour_improve(tour, neighbors, verbose, depth)
    end = time.time()
    duration = end - begin
    print "Iterations took ", duration, " seconds."
    tour.plot_paths(2 * len(tour), iteration, True, True)
    answer = raw_input("Try to improve this tour ? [Y/N] (default No) : ")
    if answer in ['Yes', 'yes', 'YES', 'y', 'Y']:
        neighbors_in = raw_input("Set a new value for neighbors count (default = actual = " + str(neighbors) + ') : ')
        if neighbors_in:
            neighbors = int(neighbors_in)
