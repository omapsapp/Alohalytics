from math import asin, cos, pi, radians, sin, sqrt

import quadkey


EARTH_RADIUS = 6367000.


def haversine(point1, point2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, point1 + point2)
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    return EARTH_RADIUS * c


def calc_lat_table():
    return {
        lat: haversine((lat, 1), (lat, 2))
        for lat in range(-90, 90)
    }


_lat_table = {}


def in_close_proximity(point1, point2, delta):
    global _lat_table

    lat = round(point1[0], 0)
    lat_1_dist = 111125.
    try:
        lon_1_dist = _lat_table[delta][lat]
    except KeyError:
        _lat_table[delta] = calc_lat_table()
        lon_1_dist = _lat_table[delta][lat]

    lon_delta = delta / lon_1_dist
    lat_delta = delta / lat_1_dist

    if point1[0] - lat_delta <= point2[0] <= point1[0] + lat_delta and\
            point1[1] - lon_delta <= point2[1] <= point1[1] + lon_delta:
        return True
    return False


def get_point_and_neighbours(lat, lon, distance):
    lat_delta = (distance / EARTH_RADIUS) * (180 / pi)
    lon_delta = lat_delta / cos(lat * pi / 180)

    return (
        (lat, lon),
        (lat, lon + lon_delta),
        (lat, lon - lon_delta),
        (lat + lat_delta, lon),
        (lat - lat_delta, lon)
    )

# megapolis zoom level
QUAD_LEVEL = 9


def get_quadint(lat, lon, level=QUAD_LEVEL):
    return int(str(quadkey.lonlat2quadint(lon, lat))[:level])


def get_quad_and_neighbours(lat, lon, distance):
    return frozenset(
        get_quadint(*p)
        for p in get_point_and_neighbours(lat, lon, distance)
    )


def split_quad(quadint):
    quad = str(quadint)
    return quad[:5], quad[5:9], quad[9:]
