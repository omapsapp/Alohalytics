"""Data structures for use by geosearch."""


class BaseBinaryEventsStorage(object):
    """Base class for a storage for binary events with fixed length."""

    record_size = None

    @classmethod
    def deserialize_event(cls, bin_str):
        """To implement in a child. How to deserialize specific saved data."""
        raise NotImplementedError

    def load_geo_index(self, index_fpath):
        """To implement in a child. How to load geo index data as a dict."""
        raise NotImplementedError

    def dump_events(self, fpath, lines):
        """Bulk save."""
        with open(fpath, 'wb') as fout:
            fout.write(''.join(lines))

    def calc_offsets(self, lines, geoindexed):
        """Byte offset calculation for every saved record."""
        return (
            (line_no * self.record_size, quad)
            for line_no, quad in enumerate(
                e.quad for e in geoindexed
            )
        )

    def open_file(self, fpath):
        """Storage file open wrapper."""
        return open(fpath, 'rb')

    def read_events(self, finput, event_num):
        """In memory loading of the events."""
        block = finput.read(self.record_size * event_num)
        offsets = range(0, event_num * self.record_size, self.record_size)
        return [
            self.deserialize_event(block[offset:offset + self.record_size])
            for offset in offsets
        ]

    def move_to_offset(self, finput, offset):
        """Seek in the storage file implementation."""
        return finput.seek(offset)
