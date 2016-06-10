from pyaloha.event import Event, DictEvent


class RouteRequest(DictEvent):
    keys = (
        'Routing_CalculatingRoute',
    )

    def __init__(self, *args, **kwargs):
        super(RouteRequest, self).__init__(*args, **kwargs)

        self.start = self.user_info.get_location() or (
            self.data['startLat'], self.data['startLon']
        )

        try:
            self.destination = (
                self.data['finalLat'], self.data['finalLon']
            )
        except KeyError:
            self.destination = None

        # vehicle, astar-bidirectional-pedestrian
        self.mode = self.data.get('name', self.data.get('router'))
        if self.mode in ('astar-bidirectional-pedestrian',):
            self.mode = 'pedestrian'

    def process_me(self, processor):
        processor.process_routing(self)


class RouteStart(Event):
    keys = (
        'Routing. Start',
    )

    def process_me(self, processor):
        processor.process_routing(self)


class RouteEnd(DictEvent):
    keys = (
        'RouteTracking_RouteClosing',
        'RouteTracking_ReachedDestination'
    )

    def __init__(self, *args, **kwargs):
        super(RouteEnd, self).__init__(*args, **kwargs)

        self.percent = float(self.data.get('percent', 100))

    def process_me(self, processor):
        processor.process_routing(self)


class RouteTracking(Event):
    keys = (
        'RouteTracking_PercentUpdate',
    )

    def __init__(self, *args, **kwargs):
        super(RouteTracking, self).__init__(*args, **kwargs)

    def process_me(self, processor):
        processor.process_routing(self)
