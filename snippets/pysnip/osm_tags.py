"""Module defines osm tags convert functions and mappings."""

import os

from mapsme_tags import MapsMeTags

# secondary tags that define additional info about object
# add to the end of the list to be compatible with already
# collected data
SECONDARY_TAGS = (
    'amenity-atm',
    'amenity-bench',
    'amenity-toilets',
    'area:highway',
    'area:highway-footway',
    'area:highway-living_street',
    'area:highway-path',
    'area:highway-pedestrian',
    'area:highway-primary',
    'area:highway-residential',
    'area:highway-secondary',
    'area:highway-service',
    'area:highway-steps',
    'area:highway-tertiary',
    'area:highway-unclassified',
    'boundary-administrative-10',
    'boundary-administrative-11',
    'boundary-administrative-2',
    'boundary-administrative-3',
    'boundary-administrative-4',
    'boundary-administrative-4-state',
    'boundary-administrative-5',
    'boundary-administrative-6',
    'boundary-administrative-7',
    'boundary-administrative-8',
    'boundary-administrative-9',
    'boundary-administrative-city',
    'boundary-administrative-country',
    'boundary-administrative-county',
    'boundary-administrative-municipality',
    'boundary-administrative-nation',
    'boundary-administrative-region',
    'boundary-administrative-state',
    'boundary-administrative-suburb',
    'boundary-national_park',
    'cuisine-african',
    'cuisine-american',
    'cuisine-arab',
    'cuisine-argentinian',
    'cuisine-asian',
    'cuisine-bagel',
    'cuisine-balkan',
    'cuisine-barbecue',
    'cuisine-bavarian',
    'cuisine-beef_bowl',
    'cuisine-brazilian',
    'cuisine-breakfast',
    'cuisine-burger',
    'cuisine-buschenschank',
    'cuisine-cake',
    'cuisine-caribbean',
    'cuisine-chicken',
    'cuisine-chinese',
    'cuisine-coffee_shop',
    'cuisine-crepe',
    'cuisine-croatian',
    'cuisine-curry',
    'cuisine-deli',
    'cuisine-diner',
    'cuisine-donut',
    'cuisine-ethiopian',
    'cuisine-filipino',
    'cuisine-fine_dining',
    'cuisine-fish',
    'cuisine-fish_and_chips',
    'cuisine-french',
    'cuisine-friture',
    'cuisine-georgian',
    'cuisine-german',
    'cuisine-greek',
    'cuisine-grill',
    'cuisine-heuriger',
    'cuisine-hotdog',
    'cuisine-hungarian',
    'cuisine-ice_cream',
    'cuisine-indian',
    'cuisine-indonesian',
    'cuisine-international',
    'cuisine-irish',
    'cuisine-italian',
    'cuisine-italian_pizza',
    'cuisine-japanese',
    'cuisine-kebab',
    'cuisine-korean',
    'cuisine-lao',
    'cuisine-lebanese',
    'cuisine-local',
    'cuisine-malagasy',
    'cuisine-malaysian',
    'cuisine-mediterranean',
    'cuisine-mexican',
    'cuisine-moroccan',
    'cuisine-noodles',
    'cuisine-oriental',
    'cuisine-pancake',
    'cuisine-pasta',
    'cuisine-persian',
    'cuisine-peruvian',
    'cuisine-pizza',
    'cuisine-polish',
    'cuisine-portuguese',
    'cuisine-ramen',
    'cuisine-regional',
    'cuisine-russian',
    'cuisine-sandwich',
    'cuisine-sausage',
    'cuisine-savory_pancakes',
    'cuisine-seafood',
    'cuisine-soba',
    'cuisine-spanish',
    'cuisine-steak_house',
    'cuisine-sushi',
    'cuisine-tapas',
    'cuisine-tea',
    'cuisine-thai',
    'cuisine-turkish',
    'cuisine-vegan',
    'cuisine-vegetarian',
    'cuisine-vietnamese',
    'emergency-defibrillator',
    'emergency-fire_hydrant',
    'emergency-phone',
    'event-fc2018',
    'event-fc2018_city',
    'hwtag-lit',
    'hwtag-oneway',
    'hwtag-private',
    'hwtag-toll',
    'internet_access',
    'internet_access-wlan',
    'olympics-attraction',
    'olympics-bike_sport',
    'olympics-live_site',
    'olympics-official_building',
    'olympics-stadium_main',
    'olympics-transport_airport',
    'olympics-transport_boat',
    'olympics-transport_bus',
    'olympics-transport_cable',
    'olympics-transport_railway',
    'olympics-transport_subway',
    'olympics-transport_tram',
    'olympics-water_sport',
    'piste:lift-j-bar',
    'piste:lift-magic_carpet',
    'piste:lift-platter',
    'piste:lift-rope_tow',
    'piste:lift-t-bar',
    'piste:type-downhill',
    'piste:type-downhill-advanced',
    'piste:type-downhill-easy',
    'piste:type-downhill-expert',
    'piste:type-downhill-freeride',
    'piste:type-downhill-intermediate',
    'piste:type-downhill-novice',
    'piste:type-nordic',
    'piste:type-sled',
    'psurface-paved_bad',
    'psurface-paved_good',
    'psurface-unpaved_bad',
    'psurface-unpaved_good',
    'sponsored-banner-deliveryclub',
    'sponsored-banner-geerbest_de',
    'sponsored-banner-geerbest_fr',
    'sponsored-banner-geerbest_uk',
    'sponsored-banner-lamoda_ru',
    'sponsored-banner-lamoda_ua',
    'sponsored-banner-raileurope',
    'sponsored-banner-rentalcars',
    'sponsored-banner-tutu',
    'sponsored-banner-viator',
    'sponsored-booking',
    'sponsored-cian',
    'sponsored-halloween',
    'sponsored-holiday',
    'sponsored-opentable',
    'sponsored-partner1',
    'sponsored-partner10',
    'sponsored-partner12',
    'sponsored-partner18',
    'sponsored-partner19',
    'sponsored-partner2',
    'sponsored-partner20',
    'sponsored-partner3',
    'sponsored-partner4',
    'sponsored-partner5',
    'sponsored-partner6',
    'sponsored-partner7',
    'sponsored-partner8',
    'sponsored-partner9',
    'sponsored-thor',
    'sponsored-tinkoff',
    'sponsored-viator',
    'sport-american_football',
    'sport-archery',
    'sport-athletics',
    'sport-australian_football',
    'sport-baseball',
    'sport-basketball',
    'sport-bowls',
    'sport-cricket',
    'sport-curling',
    'sport-diving',
    'sport-equestrian',
    'sport-football',
    'sport-golf',
    'sport-gymnastics',
    'sport-handball',
    'sport-multi',
    'sport-scuba_diving',
    'sport-shooting',
    'sport-skiing',
    'sport-soccer',
    'sport-swimming',
    'sport-tennis',
    'tourism-attraction',
    'tourism-artwork',
    'tourism-attraction-animal',
    'tourism-attraction-specified',
    'tourism-museum',
    'tourism-gallery',
    'tourism-viewpoint',
    'traffic_calming',
    'wheelchair',
    'wheelchair-limited',
    'wheelchair-no',
    'wheelchair-yes'
)


assert len(SECONDARY_TAGS) < 2 ** 8

_base_path = os.path.dirname(os.path.abspath(__file__))
_classifier_path = os.path.join(
    _base_path, '..', '..', 'omim', 'data', 'classificator.txt'
)

_all_tags = MapsMeTags(_classifier_path).tags
_secondary_set = frozenset(SECONDARY_TAGS)

PRIMARY_TAGS = tuple(
    tag
    for tag in _all_tags
    if tag not in _secondary_set
)

del _secondary_set
del _all_tags

assert len(PRIMARY_TAGS) < 2 ** 16

# defining groups of tags
# sorted by popularity
GROUPS = (
    ('roads', frozenset((
        'highway-pedestrian',
        'highway-pedestrian-area',
        'highway-unclassified',
        'highway-motorway',
        'highway-trunk',
        'highway-primary',
        'highway-tertiary',
        'highway-secondary',
        'highway-residential'
    ))),
    ('hotels', frozenset((
        'tourism-hotel',
        'tourism-hostel',
        'tourism-apartment',
        'tourism-guest_house',
        'tourism-resort',
        'tourism-camp_site'
    ))),
    ('hotels_all', frozenset((
        'tourism-apartment',
        'tourism-camp_site',
        'tourism-chalet',
        'tourism-guest_house',
        'tourism-hostel',
        'tourism-hotel',
        'tourism-motel',
        'tourism-resort',
    ))),
    ('food', frozenset((
        'amenity-bar',
        'amenity-fast_food',
        'amenity-cafe',
        'amenity-restaurant',
        'amenity-pub',
        'shop-bakery'
    ))),
    ('city_transport', frozenset((
        'railway-station-subway',
        'railway-subway_entrance',
        'railway-tram_stop',
        'highway-bus_stop'
    ))),
    ('global_transport', frozenset((
        'aeroway-aerodrome',
        'aeroway-aerodrome-international',
        'aerialway-station',
        'amenity-ferry_terminal',
        'railway-halt',
        'railway-station',
        'building-train_station',
        'amenity-bus_station'
    ))),
    ('personal_transport', frozenset((
        'amenity-parking',
        'amenity-parking-fee',
        'amenity-fuel',
        'highway-service'
    ))),
    ('large_toponyms', frozenset((
        'place-region',
        'place-locality',
        'place-hamlet',
        'place-continent',
        'place-state',
        'place-state-USA',
        'place-city-capital-6',
        'place-city-capital-4',
        'place-city-capital-2',
        'place-city-capital',
        'place-suburb',
        'place-country',
        'place-city',
        'place-town',
        'place-village',
        'place-island'
    ))),
    ('sightseeing', frozenset((
        'tourism-zoo',
        'man_made-lighthouse',
        'amenity-fountain',
        'waterway-waterfall',
        'natural-cave_entrance',
        'historic-castle',
        'historic-castle-stately',
        'historic-castle-defensive',
        'tourism-artwork',
        'tourism-artwork-statue',
        'tourism-artwork-sculpture',
        'tourism-attraction',
        'tourism-viewpoint',
        'tourism-museum',
        'tourism-zoo',
        'historic-memorial',
        'historic-memorial-statue',
        'amenity-place_of_worship',
        'amenity-place_of_worship-christian',
        'amenity-place_of_worship-buddhist',
        'amenity-place_of_worship-hindu',
        'amenity-place_of_worship-jewish',
        'amenity-place_of_worship-shinto',
        'amenity-place_of_worship-taoist',
        'amenity-place_of_worship-muslim',
        'natural-peak',
        'amenity-theatre',
        'boundary-national_park',
        'tourism-theme_park',
        'natural-beach',
        'natural-volcano',
        'natural-water',
        'natural-spring',
        'natural-geyser',
        'historic-monument',
        'historic-archaeological_site',
        'historic-ruins',
        'leisure-park',
        'leisure-nature_reserve',
        'leisure-garden',
        'leisure-water_park',
        'place-square',
        'amenity-arts_centre'
    ))),
    ('shopping', frozenset((
        'shop-clothes',
        'amenity-marketplace',
        'shop',
        'shop-convenience',
        'shop-mall',
        'shop-supermarket',
        'shop-department_store',
        'shop-books',
        'shop-shoes',
        'shop-sports'
    ))),
    ('greenzone', frozenset((
        'landuse-forest',
        'natural-wood',
        'landuse-farmland',
        'landuse-meadow'
    ))),
    ('health', frozenset((
        'amenity-pharmacy',
        'amenity-hospital',
        'amenity-clinic',
        'amenity-dentist',
        'amenity-doctors'
    )))
)


def get_group_by_tag(tag):
    """Match tag to the appropriate group."""
    for group, tag_set in GROUPS:
        if tag in tag_set:
            return group


_PRIMARY_SET = {tag: index for index, tag in enumerate(PRIMARY_TAGS)}
_SECONDARY_SET = {tag: index for index, tag in enumerate(SECONDARY_TAGS)}


class TaggedOSMObject(object):
    """Numeric representation for the tags."""

    _primary_set_inverted = PRIMARY_TAGS
    _secondary_set_inverted = SECONDARY_TAGS

    _max_primary_num = 3
    """Primary numbers are larger so we try to minimize them.
    This num is allowed. Others are randomly cut off."""
    _max_secondary_num = 7
    """Max number for secondary tags. We will randomly cut excessive tags."""
    __fixed_binary_format__ = 'H' * _max_primary_num + 'B' * _max_secondary_num

    def __init__(self, tags=None):
        """
        Default constructor.

        If string tags are provided - they will be imported
        """
        if tags is not None:
            self._import_tags(tags)

        self.primary_tags = tuple()
        self.secondary_tags = tuple()

    def _import_tags(self, tags):
        secondary_tags = []
        primary_tags = []
        is_building = False
        for tag in sorted(tags):
            try:
                secondary_tags.append(_SECONDARY_SET[tag])
            except KeyError:
                if tag == 'building':
                    is_building = True
                    continue

                try:
                    primary_tags.append(_PRIMARY_SET[tag])
                except KeyError:
                    pass

        if not primary_tags and is_building:
            primary_tags = [_PRIMARY_SET['building']]
        else:
            # we have a little number of places with excessive tagging
            primary_tags = primary_tags[:self._max_primary_num]

        # we have a little number of places with excessive tagging
        secondary_tags = secondary_tags[:self._max_secondary_num]

        self.primary_tags = tuple(primary_tags)
        self.secondary_tags = tuple(secondary_tags)

    @classmethod
    def get_numeric_tag(cls, string_tag):
        """
        Get a numeric pair for the string tag.

        First element reserved for the primary tags,
        second for the secondary.
        """
        return _PRIMARY_SET.get(string_tag), _SECONDARY_SET.get(string_tag)

    def has_tag(self, string_tag):
        """Used for comparison of tags of different representations."""
        primary, secondary = self.get_numeric_tag(string_tag)
        return primary in self.primary_tags or secondary in self.secondary_tags

    def is_superset(self, other):
        """Check if another object tags are included in the current object."""
        tags = self.tags
        for t in other.tags:
            if t not in tags:
                return False
        return True

    def export_primary_tags(self):
        """Get string values for the primary tags."""
        return tuple(
            self._primary_set_inverted[t]
            for t in self.primary_tags
        )

    def export_secondary_tags(self):
        """Get string values for the secondary tags."""
        return tuple(
            self._secondary_set_inverted[t]
            for t in self.secondary_tags
        )

    @property
    def tags(self):
        """Get all tags in their numerical representation."""
        return self.primary_tags + self.secondary_tags

    def __gen_fixed_values__(self):
        """Generate fixed length iterable."""
        for tag in self.primary_tags:
            yield tag

        for i in range(self._max_primary_num - len(self.primary_tags)):
            yield 0

        for tag in self.secondary_tags:
            yield tag

        for i in range(self._max_secondary_num - len(self.secondary_tags)):
            yield 0

    @classmethod
    def from_fixed_values(cls, values):
        """Load from a fixed values representation."""
        obj = cls()
        obj.primary_tags = values[:cls._max_primary_num]
        obj.secondary_tags = values[cls._max_primary_num:]
        return obj
