# by popularity
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
        'sponsored-booking',
        'tourism-hotel',
        'tourism-hostel',
        'tourism-apartment',
        'tourism-guest_house',
        'tourism-resort',
        'tourism-camp_site'
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
        'place-city-capital-6',
        'place-locality',
        'place-hamlet',
        'place-continent',
        'place-state',
        'place-city-capital-6',
        'place-city-capital-4',
        'place-city-capital-2',
        'place-suburb',
        'place-country',
        'place-city',
        'place-town',
        'place-village',
        'place-island'
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
        'historic-castle-stately',
        'historic-castle-defensive',
        'tourism-artwork',
        'tourism-artwork-statue',
        'tourism-artwork-sculpture',
        'historic-memorial',
        'historic-memorial-statue',
        'amenity-place_of_worship-christian',
        'amenity-place_of_worship-buddhist',
        'amenity-place_of_worship-hindu',
        'natural-peak',
        'amenity-theatre',
        'boundary-national_park',
        'tourism-theme_park',
        'natural-beach',
        'natural-volcano',
        'natural-water',
        'natural-spring',
        'historic-monument',
        'historic-archaeological_site',
        'historic-ruins',
        'leisure-park',
        'tourism-attraction',
        'tourism-viewpoint',
        'tourism-museum',
        'leisure-nature_reserve',
        'leisure-garden',
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
        'shop-books'
    ))),
    ('greenzone', frozenset((
        'landuse-forest',
        'natural-wood',
        'landuse-farmland',
        'landuse-meadow'
    ))),
    ('health', frozenset((
        'amenity-pharmacy',
        'amenity-hospital'
    )))
)


def get_group_by_tag(tag):
    for group, tag_set in GROUPS:
        if tag in tag_set:
            return group
    return None
