import warnings
from roads import Roads
from road import Road
from matplotlib import pyplot as plt


class Tour(set):

    roads = Roads()

    # This is the heart of the data structure for the Lin-Kernighan algorithm.
    #
    # A path for the LK algorithm is a sequence of cities from 1 to N :
    #
    #   1 =>  2  => ... (i-1) => i => (i+1) ... (N-1) => N
    #
    # The path length is the sum of the (N-1) roads.  (The corresponding
    # tour distance is found by incrementing tha path length by
    # the length of the road from N to back to 1.)
    #
    # The LK algorithm works at the right end of this path, leaving
    # city 1 alone.  The idea is remove a road between some
    # city i and i+1, and then restore connectivity by connecting i to N.
    # The situation then looks like this :
    #
    #                            ----------------------------------
    #                            |                                |
    #   1 =>  2  => ... (i-1) => i    (i+1) => (i+2) ... (N-1) => N
    #
    # Then the directionality of the links from (i+1) to N is flipped
    # and the cities renumbered to get this :
    #
    #                            ---------------------------------
    #                            |                               |
    #   1 =>  2  => ... (i-1) => i     N   <= (N-1) ... (i+2) <= (i+1)
    #
    # In this implementation they don't actually have numbers;
    # instead the ordering is contained in a doubly linked list
    # using a dictionary.
    #
    #   self.first = city 1
    #   self.last = city N
    #   self.neighbors[city[i]] = (city[i-1], city[i+1])
    #
    # So to do one of these LK modifications, self.last is changed
    # and self.neighbors is modified from city i onwards.
    #
    # The Road objects don't store a direction; they just contain
    # distances, and allow for sorting by length in their Roads container.
    #
    # The rest of the L.K. algorithm is just keeping track
    # of which cities/roads are good candidates for this
    # exchange : ones that weren't in the previous tour,
    # wich make the path shorter, and (optionally) which are
    # within the M'th shortest (e.g. the shortest 5) from a city.

    @staticmethod
    def init_roads(cities):
        """
        construct all possible roads from cities list.
        The loop is like constructing a strictly upper matrix.
        """
        for index1, city1 in enumerate(cities):
            for index2, city2 in enumerate(cities[index1+1:]):
                road = Road(city1, city2)
                for obj in (Tour, city1, city2):
                    obj.roads[(city1, city2)] = road

    @staticmethod
    def get_road(city1, city2):
        return Tour.roads.get(city1, city2)

    def __init__(self, cities):

        self.cities = cities
        n = len(cities)
        roads = [Tour.get_road(self.cities[i], self.cities[(i + 1) % n]) for i in range(n)]
        super(Tour, self).__init__(roads)
        self.first = self.last = None
        self.neighbors = {}
        for i in range(n):
            self.neighbors[cities[i]] = (cities[i - 1], cities[(i + 1) % n])
        self.length = sum([road.length for road in self])

    def revert(self):
        """ Reset back to the original closed tour. """
        # The sequence of cities in self.cities isn't modified
        # during the LK modifications.
        self.__init__(self.cities)

    def close(self):
        """ Convert from an open path to a closed tour,
            keeping the city sequence generated from the LK modifications. """
        self.__init__(self.city_sequence())

    def find_lk_mods(self, max_search_roads, added=None, deleted=None):
        """ Return viable L.K. modifications as described in the ascii art above,
            stored as a list of (city_insert, road_to_add, road_to_delete), where
              1. road_to_add is city N to city i
                   optional speedup: only look at M=5 or so shortest from city N
              2. city_insert is city i, (2 <= i <= N-2) of the N cities.
                   not city N (can't go to itself);
                   not city N-1 (already in path);
              3. road_to_delete is city i to city i+1
                   since there are only two roads from city in the path,
                   and deleting i-1 to i leaves two disconnected paths
              4. road_to_add.length < road_to_delete, i.e. path improvement
              5. road_to_delete is not in added
                   i.e. don't backtrack within one L.K. K-Opt iteration
              6. road_to_add is not in 'deleted'  (in some versions of L.K.)
            There are at most N-2 of these (or at most M=5 if using that speedup),
            and likely much fewer.
        """
        if not added:
            added = set()
        if not deleted:
            deleted = set()
        mods = []
        cityN = self.last
        # Of roads from cityN, look at the at shortest, most likely roads first.
        for road_add in cityN.roads.get_by_length(max_search_roads):  # 1
            city_insert = road_add.other(cityN)
            if city_insert == self.prev_city(cityN): continue  # 2
            road_delete = Tour.get_road(city_insert, self.next_city(city_insert))  # 3
            if road_add.length >= road_delete.length: continue  # 4
            if road_delete in added: continue  # 5
            if road_add in deleted: continue  # 6
            mods.append((city_insert, road_add, road_delete))
        return mods

    def tour_length(self):
        """ Return the length of this tour or (if we're in the Path state)
            the corresponding closed TSP tour. """
        if self.is_tour():
            return self.length
        else:
            return self.length + Tour.get_road(self.first, self.last).length

    def is_forward(self, road):
        """ Return True if road[0] => road[1] is along the path,
            or if it will be once its filled in. """
        # So either road[0] => road[1]   i.e. next(0) = 1
        # or road[-1] => road[0] = None / gap / None => road[1] => road[2] .
        return self.next_city(road[0]) == road[1] or \
           self.next_city(road[0]) == None == self.prev_city(road[1])

    def is_tour(self):
        """ Return true if in original, Tour state,
            as opposed to the LK Path state. """
        return not self.first and not self.last

    def tour2path(self, road, backward=False):
        """ Convert a closed tour into an LK path by removing a road.
            If backward is true, also flip the direction of the path. """
        assert self.is_tour()
        if backward:
            self.flip_direction()
        if self.is_forward(road):
            (self.first, self.last) = (road[1], road[0])
        else:
            (self.first, self.last) = (road[0], road[1])
        self.remove(road)

    def replace_neighbors(self, road, (a, b)):
        """ Replace neighbors of road ends with new neighbors (a,b) """
        (before0, after0) = self.neighbors[road[0]]
        (before1, after1) = self.neighbors[road[1]]
        if self.is_forward(road):
            self.neighbors[road[0]] = (before0, b)
            self.neighbors[road[1]] = (a, after1)
        else:
            self.neighbors[road[1]] = (before1, a)
            self.neighbors[road[0]] = (b, after0)

    def add(self, road):
        """ Add a road. """
        super(Tour, self).add(road)
        self.length += road.length
        self.replace_neighbors(road, road)

    def remove(self, road):
        """ Remove a road. """
        super(Tour, self).remove(road)
        self.length -= road.length
        self.replace_neighbors(road, (None, None))

    def flip1city(self, city):
        """ Change directionality of neighbors of a city. """
        (before, after) = self.neighbors[city]
        self.neighbors[city] = (after, before)

    def flip_direction(self, cityA=None, cityB=None):
        if cityA:
            city = cityA
            while city:
                next_city = self.next_city(city)
                self.flip1city(city)
                if city == cityB:
                    break
                city = next_city
        else:
            for city in self.cities:
                self.flip1city(city)
            (self.first, self.last) = (self.last, self.first)

    def modify(self, city_insert, road_add, road_delete):
        """ Do LK path modification """
        # These arguments aren't independent;
        # road_add and road_delete can both be determined from city_insert.
        # but since I need all three of 'em in find_lk_mods and here,
        # it seems simplest to just pass all of 'em around.
        #
        # Here's the picture of what's going on, copied from up above.
        #                            ----------------------------------
        #                            |                                |
        #   1 =>  2  => ... (i-1) => i    (i+1) => (i+2) ... (N-1) => N
        #
        #   city_insert  is  city[i]
        #   self.last    is  city[N]
        #   road_add     is  city[N] => city[i] (over the top);
        #   road_delete  is  city[i] => i+1
        #
        iPlus1 = road_delete.other(city_insert)
        cityN = self.last
        if not road_delete in self:
            raise Exception("Oops - tried to remove %s from %s" % (str(road_delete), ",".join(map(str, self))))
        self.remove(road_delete)
        self.flip_direction(iPlus1, cityN)
        self.add(road_add)
        self.last = iPlus1

    def unmodify(self, city_insert, road_add, road_delete):
        """ Undo LK path modification """
        # See the picture above; I'm using the original numbering scheme.
        iPlus1 = self.last
        cityN = road_add.other(city_insert)
        if not road_add in self:
            raise Exception("Oops - tried to remove %s from set %s" % (str(road_add), ",".join(map(str, self))))
        self.remove(road_add)
        self.flip_direction(cityN, iPlus1)
        self.add(road_delete)
        self.last = cityN

    def next_city(self, city):
        return self.neighbors[city][1]

    def prev_city(self, city):
        return self.neighbors[city][0]

    def city_sequence(self):
        """ Return the cities along the path from first to last,
            or the cities in the tour. """
        if not self.first and not self.last:
            return self.cities
        else:
            cities = []
            city = self.first
            while True:
                cities.append(city)
                if city == self.last:
                    break
                city = self.next_city(city)
            return cities

    def plot_cities(self):
        """ Plot Tour cities in a figure.
        This method is called only once as long as the figure is not closed,
        because the cities are the same, only paths change.
        """
        x = []
        y = []
        for city in self.city_sequence():
            x.append(city.x)
            y.append(city.y)
            plt.annotate(city.name, xy=(city.x, city.y), xytext=(5, 5), textcoords='offset points')

        plt.plot(x, y, 'co')

        # Ignore matplotlib warnings related to GUI
        warnings.filterwarnings("ignore", ".*GUI.*")

    def plot_paths(self, iteration, best_iteration, block=False, end=False):
        """Plot paths between cities plotted previously
        """
        cities = self.city_sequence()
        for index in range(len(cities) - 1):
            plt.arrow(cities[index].x, cities[index].y, (cities[index+1].x - cities[index].x),
                      (cities[index+1].y - cities[index].y), color='r',
                      length_includes_head=True, head_width=0, width=0.001)

        if self.is_tour():
            plt.arrow(cities[-1].x, cities[-1].y, (cities[0].x - cities[-1].x), (cities[0].y - cities[-1].y),
                      head_width=0, color='r', length_includes_head=True, width=0.001)
        plt.suptitle('Actual iteration : ' + str(iteration) + '/' + str(2*len(self)) +
                     '\n Best tour found on iteration : '
                     + str(best_iteration) + ', Tour length : ' + str(self.tour_length()), fontsize=12)
        ax = plt.gca()
        if end:
            plt.text(0.5, -0.1, 'Finished, Close this window to stop the program.', horizontalalignment='center',
                     verticalalignment='center', transform=ax.transAxes, color='green', weight='bold')
        plt.show(block)
        plt.pause(0.1)
        del ax.artists[:]

    def __str__(self):
        cities_along_path = self.city_sequence()
        names = [c.name for c in cities_along_path]
        if len(names) > 8:
            names[3:-3] = ['...']
        city_string = " - ".join(names)
        if len(self.cities) == len(self):
            city_string += " - " + cities_along_path[0].name
            return "<Tour (%i roads, length %4.2f): %s>" % \
                   (len(self), self.length, city_string)
        else:
            return "<Path (%i roads, length %4.2f, tour %4.2f): %s>" % \
                   (len(self), self.length, self.tour_length(), city_string)