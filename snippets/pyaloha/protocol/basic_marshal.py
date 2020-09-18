import marshal
import multiprocessing
import traceback
import sys


from pyaloha.protocol.base import WorkerResults, custom_loads

if sys.version_info[0] == 3:
    from collections.abc import Iterable, Mapping
else:
    from collections import Iterable, Mapping


class MarshalWorkerResults(WorkerResults):
    @classmethod
    def to_basic_types(cls, obj):
        if hasattr(obj, '__dumpdict__'):
            obj = obj.__dumpdict__()
        elif isinstance(obj, Mapping):
            obj = {
                key: cls.to_basic_types(value)
                for key, value in obj.items()
            }
        elif isinstance(obj, Iterable) and not isinstance(obj, (str, bytes)):
            obj = [
                cls.to_basic_types(sub_obj)
                for sub_obj in obj
            ]
        return obj

    @classmethod
    def from_basic_types(cls, obj):
        if isinstance(obj, Mapping):
            _obj = custom_loads(obj)
            if obj is _obj:
                obj = {
                    key: cls.from_basic_types(value)
                    for key, value in obj.items()
                }
            else:
                obj = _obj
        elif isinstance(obj, Iterable) and not isinstance(obj, (str, bytes)):
            obj = [
                cls.from_basic_types(sub_obj)
                for sub_obj in obj
            ]
        return obj

    @classmethod
    def dumps(cls, obj, debug=False):
        return marshal.dumps(cls.to_basic_types(obj))

    @classmethod
    def loads(cls, data):
        try:
            return cls.from_basic_types(marshal.loads(data))
        except Exception as err:
            logger = multiprocessing.get_logger()
            logger.error('Corrupted data of len:\n%s' % len(data))
            traceback.print_exc(err)
            return []
