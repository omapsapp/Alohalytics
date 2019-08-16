from __future__ import division

from itertools import chain
from math import asin, cos, radians, sin, sqrt, pi, log

from quadkey import (
    xyz2quadint, tiles_intersecting_webmercator_box, lonlat2xy,
    xy2webmercator, tile_children
)


# in meters
EARTH_RADIUS = 6367000.
# 1 degree latitude in meters
LAT_1_DISTANCE = 111136.
# megapolis zoom level
QUAD_LEVEL = 9
# min number of digits in geohash
GEOHASH_MIN_LEVEL = 17
TILE_MAX_ZOOM = 20


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
    table = {}
    for _lat in range(-900, 901):
        lat = round(0.1 * _lat, 1)
        table[lat] = haversine((lat, 1), (lat, 2))
    return table

_lat_table = calc_lat_table()


def get_small_deltas(point1, delta):
    global _lat_table

    lat = round(point1[0], 1)
    lon_1_dist = _lat_table[lat]

    return round(delta / LAT_1_DISTANCE, 7), round(delta / lon_1_dist, 7)


def in_close_proximity(point1, point2, delta):
    lat_delta, lon_delta = get_small_deltas(point2, delta)

    if point1[0] - lat_delta <= point2[0] <= point1[0] + lat_delta and\
            point1[1] - lon_delta <= point2[1] <= point1[1] + lon_delta:
        return True
    return False


def get_neighbour_bbox(lat, lon, small_distance):
    lat_delta, lon_delta = get_small_deltas((lat, lon), small_distance)

    return (
        lat - lat_delta, lon - lon_delta,
        lat + lat_delta, lon + lon_delta
    )


def get_quadint(lat, lon, zoom=TILE_MAX_ZOOM):
    fx = (lon + 180.0) / 360.0
    sinlat = sin(lat * pi / 180.0)
    fy = 0.5 - log((1 + sinlat) / (1 - sinlat)) / (4 * pi)
    mapsize = (1 << zoom)
    x = int(fx * mapsize)
    y = int(fy * mapsize)

    return xyz2quadint(x, y, zoom)


def _flat_quads(quads, target_zoom):
    for q, z in quads:
        _quads = [q]
        while z < target_zoom:
            _quads = list(chain.from_iterable(map(
                lambda q: tile_children(q, z),
                _quads
            )))
            z += 1
        for _q in _quads:
            yield _q


# This function assumes that target_zoom is the most detailed zoom in the input
def flat_quads(quads, target_zoom):
    good = [
        q
        for q, z in quads
        if z == target_zoom
    ]
    if len(good) == len(quads):
        return good

    to_split = filter(lambda x: x[1] < target_zoom, quads)
    return chain(good, _flat_quads(to_split, target_zoom))


def get_quads_around(lat, lon, distance, zoom=TILE_MAX_ZOOM):
    lat_l, lon_l, lat_h, lon_h = get_neighbour_bbox(lat, lon, distance)
    x_l, y_l = lonlat2xy(lon_l, lat_l)
    x_h, y_h = lonlat2xy(lon_h, lat_h)
    lat_l, lon_l = xy2webmercator(x_l, y_l)
    lat_h, lon_h = xy2webmercator(x_h, y_h)
    return flat_quads(
        tiles_intersecting_webmercator_box(zoom, lat_l, lon_l, lat_h, lon_h),
        target_zoom=zoom
    )


def split_quad(quadint, tail_level=QUAD_LEVEL):
    quad = str(quadint)
    return [quad]
    # return quad[:4], quad[4:]


def get_quad_tail(lat, lon, tail_level):
    return extract_quad_tail(
        get_quadint(lat, lon), tail_level
    )


def extract_quad_head(quadint, tail_level=QUAD_LEVEL):
    return quadint >> 2 * (31 - tail_level)


def extract_quad_tail(quadint, tail_level=QUAD_LEVEL):
    mask = (1 << 2 * (31 - tail_level)) - 1
    return quadint & mask


def split_quad_by_two(quadint, tail_level=QUAD_LEVEL):
    bits = 2 * (31 - tail_level)
    return (
        quadint >> bits,
        quadint & ((1 << bits) - 1)
    )
