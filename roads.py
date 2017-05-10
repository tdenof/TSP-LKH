class Roads(dict):
    """ A collection of roads with
          * no duplicates
          * no city sequence
          * access by city pairs
          * access to other city from a given one
          * modifications via roads.add(road), roads.remove(road)
          * optional ordering by road length
        This is designed to be both
          * a data structure for all the roads in a TSP,
          * a base class for the Tour object used in the LK algorithm.
    """
    def __init__(self, roads=None):
        if not roads:
            roads = {}
        super(Roads, self).__init__(roads)
        self.by_length = None

    def get(self, city1, city2):
        return super(Roads, self).get((city1, city2), super(Roads, self).get((city2, city1), None))

    def get_by_length(self, count=None):
        if not self.by_length:
            self.by_length = self.values()
            self.by_length.sort()
        return self.by_length[:count]
