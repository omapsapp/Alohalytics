from pyaloha.event import Event, DictEvent
from pyaloha.ccode import c_string, c_unicode


# ALOHA: searchEmitResults [
#   blida trib=8
# ]
#
# ALOHA (after Feb 2016): searchEmitResultsAndCoords [
#   posX=-71.9772 posY=-13.642 query=pizze results=10
#   Pizzeria|Restaurant|0   Don Angelo Pizzeria|Restaurant|0
#   viewportMaxX=-71.9639 viewportMaxY=-13.6282
#   viewportMinX=-71.998 viewportMinY=-13.663
# ]

class SearchResults(DictEvent):
    keys = (
        'searchEmitResults', 'searchEmitResultsAndCoords'
    )

    def __init__(self, *args, **kwargs):
        super(SearchResults, self).__init__(*args, **kwargs)

        try:
            self.query = self.data['query']
        except KeyError as old_type_event:
            self.query, self.result_num = self.data.items()[0]
        else:
            results = filter(None, self.data['results'].split())
            self.result_num = int(results[0])
            self.results = results[1:]

    def process_me(self, processor):
        processor.process_search_results(self)

    def __dumpdict__(self):
        d = super(DictEvent, self).__dumpdict__()

        d['query'] = self.query
        d['result_num'] = self.result_num
        return d


class GPSTracking(Event):
    keys = (
        'Flurry:logLocation', 'Framework:EnterBackground'
    )

    def __init__(self, *args, **kwargs):
        super(GPSTracking, self).__init__(*args, **kwargs)

        self.data_list = None

    def process_me(self, processor):
        processor.process_gps_tracking(self)
