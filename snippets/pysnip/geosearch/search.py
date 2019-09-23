"""Search functions operating on the collected popularity data."""

from __future__ import division

import collections
import multiprocessing
import os

from itertools import groupby, chain

from operator import itemgetter

from pysnip.fs_utils import gen_quad_dir

from pysnip.geo_utils import (
    get_quads_around, in_close_proximity,
    split_quad_by_two
)

from pydataproc.procs.intensive_pool import Pool


def _quad_search(item):
    quad, points, settings = item
    quad_root_dir, proximity_delta_meters, quad_dir_level = settings

    proc = DataProcessor(quad_root_dir, proximity_delta_meters)
    return proc.quad_search(quad, points)


def _aggregate_by_quads(tasks, pool):
    return aggregate_by_quads_impl(tasks, pool, _quad_calc_worker)


def _quad_calc_worker(item):
    i, ((lat, lon, tag), settings) = item
    tags = None if tag is None else [tag]
    return quad_calc_worker_impl(i, (lat, lon), tags, settings)


VERY_LARGE_NUMBER = 10 ** 6


class BaseSearcher(Pool):
    """Multiproc geo search class."""

    def __init__(self, root_dir, quad_dir_level,
                 batch_size=VERY_LARGE_NUMBER,
                 quad_search=_quad_search, quad_aggregate=_aggregate_by_quads):
        """Constructor. Starts multiple processes."""
        self.root_dir = root_dir
        self.quad_dir_level = quad_dir_level
        super(BaseSearcher, self).__init__(
            dispatchers_num=3,
            batch_size=batch_size
        )

        self.quad_search = quad_search
        self.quad_aggregate = quad_aggregate

    def search_by_geo(self, geopoints, proximity_delta_meters):
        """Bulk geo search."""
        settings = (self.root_dir, proximity_delta_meters, self.quad_dir_level)
        geopoints = [
            (p, settings)
            for p in geopoints
        ]
        results = self.map(self.quad_search, geopoints,
                           shuffle_func=self.quad_aggregate)

        del geopoints

        return results


class EventsFilter(object):
    """Class to filter events by geo and tags (optional)."""

    def __init__(self, proximity_delta_meters):
        """Simple constructor."""
        self.proximity_delta_meters = proximity_delta_meters

    def is_close_enough(self, event, point):
        """Define close proximity."""
        return in_close_proximity(
            event.point, point,
            delta=self.proximity_delta_meters
        )

    def has_tags(self, event, tags):
        """If tags filter needed child can implement it."""
        return True

    def check(self, event, point, tags=None):
        """Superposition of has_tags and is_close_enough."""
        return (
            self.is_close_enough(event, point) and
            self.has_tags(event, tags)
        )


class DataProcessor(object):
    """Quad directory data processor to be customized by a child."""

    def __init__(self, quad_root_dir, proximity_delta_meters):
        """Simple constructor."""
        self.quad_root_dir = quad_root_dir
        self.proximity_delta_meters = proximity_delta_meters
        self.events_filter_check = EventsFilter(proximity_delta_meters).check
        self.events_storage = None

    def quad_search(self, quad, points):
        """Get filtered events from a quad."""
        stats = collections.Counter()

        quad_dir = gen_quad_dir(quad, root_dir=self.quad_root_dir)
        try:
            _mfiles = os.listdir(quad_dir)
        except OSError:
            stats['no_quad_found'] += 1
            stats['record_count'] += len(points)
            return [], dict(stats)

        sorted_indexed_points = sorted(points)

        # use only files without extention
        mfiles = [f for f in _mfiles if len(f.rsplit('.', 1)) == 1]

        def process_file(month_file):
            month_file = os.path.join(quad_dir, month_file)
            _candidates = self._process_month_file(
                month_file, sorted_indexed_points
            )
            stats['record_count'] += len(sorted_indexed_points)
            return _candidates

        candidates = chain.from_iterable(
            process_file(month_file)
            for month_file in mfiles
        )

        candidates = sorted(candidates)
        candidates = [
            (index, list(chain.from_iterable(
                events for _, events in grouped
            )))
            for index, grouped in groupby(candidates, key=itemgetter(0))
        ]

        return candidates, dict(stats)

    def _process_month_file(self, month_file, sorted_indexed_points):
        index_fpath = month_file + '.geo'

        quads_to_lines = self.events_storage.load_geo_index(index_fpath)

        with self.events_storage.open_events_file_readonly(month_file) as fin:
            # use that events in this file are sorted by their quads
            grouped = groupby(sorted_indexed_points, key=itemgetter(0))
            for quad, points in grouped:
                # get offset and number of lines inside the block
                range_position = quads_to_lines.get(quad)

                if range_position is None:
                    continue

                self.events_storage.move_to_offset(fin, range_position[0])

                # read and deserialize events from lines in range
                events = self.events_storage.read_events(
                    fin, range_position[1]
                )

                for _, index, tags, osm_point in points:
                    # filter events by tag and more accurate geo
                    results = (
                        e
                        for e in events
                        if self.events_filter_check(e, osm_point, tags)
                    )

                    if results:
                        yield index, results


def aggregate_by_quads_impl(points, pool, worker_func):
    """Aggregate points by the quad prefix."""
    quads = collections.defaultdict(list)
    calculated = pool.map(worker_func, points,
                          chunksize=(len(points) // pool._processes))
    for results in calculated:
        for qhead, point, settings in results:
            quads[qhead].append(point)

    return [
        (qhead, _points, settings)
        for qhead, _points in quads.iteritems()
    ]


def quad_calc_worker_impl(result_index, point, tags, settings):
    """Multiproc worker for a quad calculation for a point."""
    try:
        root_dir, proximity_delta_meters, quad_dir_level = settings
        quads_of_interest = get_quads_around(*point,
                                             distance=proximity_delta_meters)
        results = []
        for quad in quads_of_interest:
            quad_head, quad_tail = split_quad_by_two(quad, quad_dir_level)
            results.append(
                (quad_head, (quad_tail, result_index, tags, point), settings)
            )
        return results
    except Exception:
        logger = multiprocessing.log_to_stderr()
        logger.exception('Quad Calcultion Worker: exception')
