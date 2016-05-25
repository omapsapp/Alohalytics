import itertools

from .base import Event
from .misc import GPSTracking, SearchResults
from .onstart import AndroidVisibleLaunch, TechnicalLaunch
from .placepage import ObjectSelection
from .routing import RouteEnd, RouteRequest, RouteStart, RouteTracking


def check_events(events):
    event_keys = list(itertools.chain.from_iterable(
        event_cls.keys for event_cls in CUSTOM_EVENTS
    ))
    if len(frozenset(event_keys)) != len(event_keys):
        raise ImportError('Intersection of keys in events')


CUSTOM_EVENTS = (
    ObjectSelection,
    TechnicalLaunch, AndroidVisibleLaunch,
    SearchResults, GPSTracking,
    RouteRequest, RouteStart, RouteEnd, RouteTracking,
)


check_events(CUSTOM_EVENTS)


REGISTERED = dict(
    (key, event_cls)
    for event_cls in CUSTOM_EVENTS
    for key in event_cls.keys
)


def make_event(key, *args, **kwargs):
    return REGISTERED.get(key, Event)(key, *args, **kwargs)
