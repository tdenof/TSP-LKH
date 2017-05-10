import math


class Road(list):

    def __init__(self, city1, city2):
        super(Road, self).__init__([city1, city2])
        self.length = math.sqrt((city1.x - city2.x)**2 + (city1.y - city2.y)**2)
        self._str = "%s--%s (%4.2f)" % (self[0].name, self[1].name, self.length)
        self._id = id(self._str)

    def other(self, city):
        """ Return city at other end of road. """
        if city not in self:
            return None
        else:
            return self[1] if (self[0] == city) else self[0]

    def __str__(self):
        return self._str

    def __hash__(self):
        # Set these be OK as dictionary keys and set elements.
        # Otherwise, python is unhappy about using 'em that way,
        # since they inherit from mutable lists.
        return id(self._id)

    # And since this inherits from list, it already has <, >, etc.
    # This unfortunately means that just defining __cmp__ won't work,
    # since the others take precedence.  Python calls these "rich comparisons";
    # see http://docs.python.org/library/functools.html#functools.total_ordering
    # and http://docs.python.org/reference/datamodel.html#object.__lt__ .

    def __eq__(self, other):
        return self._str == str(other)

    # The following comparisons will fail when comparing a Road with non-Road.
    # So don't do that.

    def __lt__(self, other):
        return self.length < other.length

    def __le__(self, other):
        return self.length <= other.length

    def __gt__(self, other):
        return self.length > other.length

    def __ge__(self, other):
        return self.length <= other.length
