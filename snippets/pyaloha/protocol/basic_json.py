import json
import multiprocessing
import sys
import traceback


from pyaloha.protocol.base import WorkerResults, custom_loads


if sys.version_info[0] == 3:
    def decode_keys_for_json(dct):
        return {
            (k.decode() if isinstance(k, bytes) else k): v
            for k, v in dct.items()
        }
else:
    def decode_keys_for_json(dct):
        return dct


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__dumpdict__'):
            obj = obj.__dumpdict__()

        if isinstance(obj, dict):
            # process json unprocessable dict keys
            return decode_keys_for_json(obj)

        if not isinstance(obj, str) and isinstance(obj, bytes):
            # in python 2.7 str is bytes; don't decode it
            return obj.decode()

        # Let the base class default method raise the TypeError
        return super(CustomEncoder, self).default(obj)


class JSONWorkerResults(WorkerResults):
    @classmethod
    def dumps(cls, obj, debug=False):
        return json.dumps(
            obj, cls=CustomEncoder, ensure_ascii=False
        )

    @classmethod
    def loads(cls, data):
        try:
            return json.loads(data, object_hook=custom_loads)
        except ValueError as err:
            logger = multiprocessing.get_logger()
            logger.error('Corrupted json:\n{}'.format(data))
            traceback.print_exc(err)
            return []
