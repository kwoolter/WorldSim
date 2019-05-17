from .utils import EventQueue
from .utils import Event
from .agent import Agent

class World():

    STATE_LOADED = "LOADED"
    STATE_INITIALISED = "INITIALSED"
    STATE_DESTROYED = "DESTROYED"

    EVENT_TICK = "TICK"

    def __init__(self, name : str = "Default"):
        self.name = name
        self._state = World.STATE_LOADED
        self._tick_count = 0
        self._agents = []

    def initialise(self, name : str = "Default World"):

        if len(name) == 0:
            name = "Default World"

        self._state = World.STATE_INITIALISED
        self.name = name

        self.load_agents()

        EventQueue.add_event(Event(World.STATE_INITIALISED,
                                   "The world of '{0}' has been created!".format(self.name),
                                   Event.STATE))


    def load_agents(self):
        for i in range(0,10):
            new_agent = Agent("agent {0}".format(i), "default")
            self.add_agent(new_agent)

    def add_agent(self, new_agent : Agent):
        self._agents.append(new_agent)


    def tick(self):

        self._tick_count += 1

        for agent in self._agents:
            agent.tick()

        EventQueue.add_event(Event(World.EVENT_TICK,
                                    "World '{0}' ticked to {1}".format(self.name, self._tick_count),
                                    World.EVENT_TICK))

    def end(self):

        self._state = World.STATE_DESTROYED
        EventQueue.add_event(Event(World.STATE_DESTROYED,
                                   "The world of '{0}' has ended!".format(self.name),
                                   Event.STATE))


    def print(self):
        print("\nThe world of {0} (tick={1}).".format(self.name, self._tick_count))
        if len(self._agents) > 0:
            for agent in self._agents:
                print(str(agent))


    def get_next_event(self):

        next_event = None
        if EventQueue.size() > 0:
            next_event = EventQueue.pop_event()

        return next_event


