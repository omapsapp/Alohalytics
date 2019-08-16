"""Helpers for mapsme (omim repo) tags manipulation."""


class MapsMeTags(object):
    """/omim/master/data/classificator.txt parser.

    one public property: tags
    """

    def __init__(self, filepath):
        """Constructor and tags loader."""
        self.filepath = filepath
        with open(self.filepath) as fin:
            self.tags = self._parse(fin)

    def _parse(self, lines):
        for line in lines:
            if line.startswith('world'):
                break

        return self._expand(None, lines)

    def _expand(self, prefix, lines):
        tags = []
        while True:
            line = next(lines).strip()
            full_tag = line[:-3]
            if prefix is not None:
                full_tag = '{}-{}'.format(prefix, full_tag)

            control = line[-2:]

            if control == '{}':
                break
            if control.endswith('-'):
                tags.append(full_tag)
            elif control.endswith('+'):
                tags.extend(
                    self._expand(full_tag, lines)
                )

        return tags
