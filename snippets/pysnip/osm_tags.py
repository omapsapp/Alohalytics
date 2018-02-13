# by popularity
GROUPS = (
    ('roads', frozenset((
        'highway-pedestrian',
        'highway-pedestrian-area',
        'highway-service',
        'highway-unclassified',
        'highway-motorway',
        'highway-trunk',
        'highway-primary',
        'highway-tertiary',
        'highway-secondary',
        'highway-residential'
    ))),
    ('hotels', frozenset((
        'sponsored-booking',
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
        'railway-tram_stop',
        'highway-bus_stop'
    ))),
    ('global_transport', frozenset((
        'aeroway-aerodrome',
        'amenity-ferry_terminal',
        'railway-halt',
        'railway-station',
        'amenity-bus_station'
    ))),
    ('large_toponyms', frozenset((
        'place-region',
        'place-city-capital-6',
        'place-locality',
        'place-hamlet',
        'place-continent',
        'place-state',
        'place-city-capital-4',
        'place-city-capital-2',
        'place-suburb',
        'place-country',
        'place-city',
        'place-town',
        'place-village'
    ))),
    ('sightseeing', frozenset((
        'amenity-place_of_worship',
        'tourism-zoo',
        'man_made-lighthouse',
        'amenity-place_of_worship-muslim',
        'amenity-fountain',
        'waterway-waterfall',
        'natural-cave_entrance',
        'historic-castle',
        'tourism-artwork',
        'historic-memorial',
        'amenity-place_of_worship-christian',
        'natural-peak',
        'amenity-theatre',
        'natural-beach',
        'historic-monument',
        'leisure-park',
        'tourism-attraction',
        'tourism-viewpoint',
        'tourism-museum'
    ))),
    ('shopping', frozenset((
        'shop-clothes',
        'amenity-marketplace',
        'shop',
        'shop-convenience',
        'shop-mall',
        'shop-supermarket'
    )))
)


def get_group_by_tag(tag):
    for group, tag_set in GROUPS:
        if tag in tag_set:
            return group
    return None
