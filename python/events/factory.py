from .base import Event
from .onstart import Launch
from .routing import RouteRequest, RouteStart, RouteEnd, RouteTracking
from .misc import SearchResults, GPSTracking


CUSTOM_EVENTS = (
	Launch,
	SearchResults, GPSTracking,
	RouteRequest, RouteStart, RouteEnd, RouteTracking,
)


REGISTERED = dict(
	(key, event_cls)
	for event_cls in CUSTOM_EVENTS
	for key in event_cls.keys
)


def make_event(key, *args, **kwargs):
	return REGISTERED.get(key, Event)(key, *args, **kwargs)
