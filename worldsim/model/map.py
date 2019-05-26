import numpy
import random

class WorldMap:

    # Topo generation controls
    MAX_ALTITUDE = 10.0  # Highest Altitude
    MAX_SLOPE = MAX_ALTITUDE * 0.15  # Maximum slope
    MIN_SLOPE = MAX_SLOPE * -1.0  # Minimum slope is the negative of maximum slope
    MAX_SLOPE_DELTA = MAX_SLOPE * 2.0  # How much can the slope change
    MIN_ALTITUDE_CLIP_FACTOR = -1.0 # How many STDEV from the mean do we create a floor
    ALTITUDE_OFFSET = 0.0
    MIN_ALTITUDE = 0.0  # Lowest Altitude

    def __init__(self, name: str, width: int = 50, height: int = 50):
        self.name = name
        self._width = width
        self._height = height
        self.map = []
        self.topo_model_pass2 = []
        self.summit = (None,None)
        self.abyss = (None, None)

    def initialise(self):

        # Generate a random topology model for the map
        self.generate_topology()

        print("Altitude Data: mean:{0:.3f} stdev:{1:.3f} min:{2:.3f} max:{3:.3f}".format(self.altitude_mean,
                                                          self.altitude_std,
                                                          self.altitude_min,
                                                          self.altitude_max))

    def generate_topology(self):
        """Build a random map of altitudes using a multi-pass algorithm"""

        # Clear the topo model
        topo_model_pass1 = [[None for y in range(0, self._height)] for x in range(0, self._width)]
        self.topo_model_pass2 = [[None for y in range(0, self._height)] for x in range(0, self._width)]

        # Create an initial topography using altitudes and random slope changes
        print("Pass 1: generate altitudes and slopes...")

        # Set the first square to be a random altitude with slopes in range
        topo_model_pass1[0][0] = (random.uniform(WorldMap.MIN_ALTITUDE, WorldMap.MAX_ALTITUDE),
                                  random.uniform(WorldMap.MIN_SLOPE, WorldMap.MAX_SLOPE),
                                  random.uniform(WorldMap.MIN_SLOPE, WorldMap.MAX_SLOPE))

        for y in range(0, self._height):
            for x in range(0, self._width):
                if y == 0:
                    north_slope = random.uniform(WorldMap.MIN_SLOPE, WorldMap.MAX_SLOPE)
                    north_altitude = random.uniform(WorldMap.MIN_ALTITUDE, WorldMap.MAX_ALTITUDE)
                else:
                    north_altitude, tmp, north_slope = topo_model_pass1[x][y - 1]

                if x == 0:
                    west_slope = random.uniform(WorldMap.MIN_SLOPE, WorldMap.MAX_SLOPE)
                    west_altitude = random.uniform(WorldMap.MIN_ALTITUDE, WorldMap.MAX_ALTITUDE)
                else:
                    west_altitude, west_slope, tmp = topo_model_pass1[x - 1][y]

                clip = lambda n, minn, maxn: max(min(maxn, n), minn)

                altitude = ((north_altitude + north_slope) + (west_altitude + west_slope)) / 2
                altitude = clip(altitude, WorldMap.MIN_ALTITUDE, WorldMap.MAX_ALTITUDE)

                east_slope = west_slope + ((random.random() * WorldMap.MAX_SLOPE_DELTA) - WorldMap.MAX_SLOPE_DELTA / 2)
                east_slope = clip(east_slope, WorldMap.MIN_SLOPE, WorldMap.MAX_SLOPE)

                south_slope = north_slope + (
                            (random.random() * WorldMap.MAX_SLOPE_DELTA) - WorldMap.MAX_SLOPE_DELTA / 2)
                south_slope = clip(south_slope, WorldMap.MIN_SLOPE, WorldMap.MAX_SLOPE)

                topo_model_pass1[x][y] = (altitude, east_slope, south_slope)


        # Perform second pass averaging based on adjacent altitudes to smooth out topography
        print("Pass 2: averaging out using neighbouring points...")

        # Iterate through each point in the map
        for y in range(0, self._height):
            for x in range(0, self._width):

                # Get the height of the current point
                local_altitude_total, es, ss = topo_model_pass1[x][y]
                local_altitude_points = 1

                # Get the list of adjacent tiles
                adjacent = HexagonMaths.adjacent(x,y)

                # Get the heights of the surrounding points
                for tx, ty in adjacent:
                    if self.is_valid_xy(tx,ty) is False:
                        pass
                    else:
                        local_altitude, es, ss = topo_model_pass1[tx][ty]
                        local_altitude_total += local_altitude
                        local_altitude_points += 1

                average_altitude = (local_altitude_total / local_altitude_points)

                # Record the average altitude in a new array
                self.topo_model_pass2[x][y] = average_altitude

        # Perform 3rd pass shifting altitude to create floors in the topology at level 0
        a = numpy.array(self.topo_model_pass2)
        avg = numpy.mean(a)
        std = numpy.std(a)
        threshold = avg + (std * WorldMap.MIN_ALTITUDE_CLIP_FACTOR)
        print("Pass 3: applying altitude floor of {0:.3}...".format(threshold))
        a[a != 0] -= threshold
        self.topo_model_pass2 = a.tolist()


    @property
    def width(self):
        return self._width
        #return len(self.maps_by_theme[WorldMap.THEME_DEFAULT])

    @property
    def height(self):
        return self._height
        #return len(self.maps_by_theme[WorldMap.THEME_DEFAULT])

    # Are the specified coordinates within the area of the map?
    def is_valid_xy(self, x: int, y: int):

        result = False

        if x >= 0 and x < self._width and y >= 0 and y < self._height:
            result = True

        return result

    def get_range(self, x: int, y: int, width: int, height: int):

        a = numpy.array(self.topo_model_pass2, order="F")
        b = a[x:x + width, y:y + height]

        return b.tolist()


    # Get the altitude at the specified co-ordinates
    def get_altitude(self, x: int, y: int):
        if self.is_valid_xy(x, y) is False:
            raise Exception("Trying to get altitude at ({0},{1}) which is outside of the world!".format(x, y))
        return self.topo_model_pass2[x][y]

    # Set the altitude at the specified co-ordinates
    def set_altitude(self, new_altitude: float, x: int, y: int):
        if self.is_valid_xy(x, y) is False:
            raise Exception("Trying to set altitude at ({0},{1}) which is outside of the world!".format(x, y))
        self.topo_model_pass2[x][y] = new_altitude

    @property
    def altitude_min(self):
        return numpy.min(self.topo_model_pass2)

    @property
    def altitude_max(self):
        return numpy.max(self.topo_model_pass2)

    @property
    def altitude_mean(self):
        return numpy.mean(self.topo_model_pass2)

    @property
    def altitude_std(self):
        return numpy.std(self.topo_model_pass2)



class HexagonMaths:
    """ Helper class to navigate hexagon vectors to XY vectors"""

    # Define the names of the Hexagon vectors
    NORTH = "N"
    SOUTH = "S"
    NORTH_EAST = "NE"
    SOUTH_EAST = "SE"
    NORTH_WEST = "NW"
    SOUTH_WEST = "SW"

    # Hexagon vectors to dx,dy vectors dictionaries
    # Even X values have different vectors to odd X values
    HEX_TO_XY_EVEN = {

        NORTH : (0,-1),
        SOUTH: (0,1),
        SOUTH_EAST: (1,0),
        SOUTH_WEST:(-1,0),
        NORTH_EAST:(1,-1),
        NORTH_WEST:(-1,-1)
    }

    HEX_TO_XY_ODD = {

        NORTH : (0,-1),
        SOUTH: (0,1),
        NORTH_EAST: (1,0),
        NORTH_WEST:(-1,0),
        SOUTH_EAST:(1,1),
        SOUTH_WEST:(-1,1)
    }

    @staticmethod
    def adjacent(x : int, y : int):
        """ Return list of tiles adjacent to the specified tile"""
        adjacent_tiles = []


        if x % 2 == 0:
            vectors = HexagonMaths.HEX_TO_XY_EVEN.values()
        else:
            vectors = HexagonMaths.HEX_TO_XY_ODD.values()

        for dx,dy in vectors:
            adjacent_tiles.append(((x+dx), (y+dy)))

        return adjacent_tiles

    @staticmethod
    def is_adjacent(ax : int, ay : int, bx : int, by:int):
        " Is a specified position (ax,ay) adjacent to (bx,by)?"

        return (bx,by) in HexagonMaths.adjacent(ax, ay)

    @staticmethod
    def move_hex(origin_x : int, origin_y : int, direction : str):
        """ Return a target (x,y) position based on a origin and Hexagaon direction vector """

        if direction not in HexagonMaths.HEX_TO_XY.keys():
            raise Exception("{0}.move(): {0} is not a valid direction!".format(direction))

        if origin_x % 2 == 0:
            vectors = HexagonMaths.HEX_TO_XY_EVEN
        else:
            vectors = HexagonMaths.HEX_TO_XY_ODD

        dx,dy = vectors[direction]

        return (origin_x+dx), (origin_y+dy)

    @staticmethod
    def get_direction(origin_x : int, origin_y, target_x : int, target_y):
        """ Return the hexagon vector name from an origin to a target"""

        # If the origin and the target are not adjacent then raise an exception
        if HexagonMaths.is_adjacent(origin_x, origin_y, target_x, target_y) is False:
            raise Exception("Origin and target are not adjacent!")

        if origin_x % 2 == 0:
            vectors = HexagonMaths.HEX_TO_XY_EVEN
        else:
            vectors = HexagonMaths.HEX_TO_XY_ODD

        # Calculate the xy vector to get to the target from the origin
        dx = target_x - origin_x
        dy = target_y - origin_y

        # If the xy vector in the Hex to xy dictionary...
        if (dx,dy) in vectors.values():

            # Find the xy vector in the look-up dictionary and return the Hex vector name
            pos = list(vectors.values()).index((dx, dy))
            return list(vectors.keys())[pos]

        # Else we couldn't find a name for this vector
        else:
            return "???"

