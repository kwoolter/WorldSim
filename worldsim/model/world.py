from .utils import EventQueue
from .utils import Event

class World():

    STATE_LOADED = "LOADED"
    STATE_INITIALISED = "INITIALSED"
    STATE_DESTROYED = "DESTROYED"

    EVENT_TICK = "TICK"

    def __init__(self, name : str = "Default"):
        self.name = name
        self._state = World.STATE_LOADED
        self._tick_count = 0

    def initialise(self, name : str = "Default"):

        self._state = World.STATE_INITIALISED
        self.name = name

        EventQueue.add_event(Event(World.STATE_INITIALISED,"The world of {0} has been created!".format(self.name)))

    def tick(self):

        self._tick_count += 1

        EventQueue.add_event(Event(World.EVENT_TICK,
                                    "World ticked to {0}".format(self._tick_count),
                                    World.EVENT_TICK))

    def end(self):

        self._state = World.STATE_DESTROYED
        EventQueue.add_event(Event(World.STATE_DESTROYED, "The world of {0} has ended!".format(self.name)))


    def get_next_event(self):

        next_event = None
        if EventQueue.size() > 0:
            next_event = EventQueue.pop_event()

        return next_event

