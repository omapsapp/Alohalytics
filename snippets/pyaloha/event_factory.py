import itertools
import traceback
from collections import Counter

from pyaloha.event import get_event


class EventFactory(object):
    def __init__(self, custom_events):
        self.check_events(custom_events)

        self.registered = {
            key: event_cls
            for event_cls in custom_events
            for key in event_cls.keys
        }

    def make_event(self, key, *args, **kwargs):
        try:
            return self.registered.get(key, get_event)(key, *args, **kwargs)
        except Exception as exc:
            raise Exception(
                'Event "%s" creation failed: %s' % (
                    key, traceback.format_exc(exc)
                )
            )

    @staticmethod
    def get_duplicates(list_to_check):
        return [
            value
            for value, count in Counter(list_to_check).items()
            if count > 1
        ]


    @classmethod
    def check_events(cls, custom_events):
        event_keys = list(itertools.chain.from_iterable(
            event_cls.keys for event_cls in custom_events
        ))
        if len(frozenset(event_keys)) != len(event_keys):
            raise ImportError(
                'Keys intersection in events: {}'.format(
                    cls.get_duplicates(event_keys))
            )
