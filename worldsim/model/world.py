from .utils import EventQueue
from .utils import Event
from .agent import Agent
from .world_stats import WorldStats

class World():

    STATE_LOADED = "LOADED"
    STATE_INITIALISED = "INITIALSED"
    STATE_PLAYING = "PLAYING"
    STATE_PAUSED = "PAUSED"
    STATE_DESTROYED = "DESTROYED"

    EVENT_TICK = "TICK"

    def __init__(self, name : str = "Default"):
        self.name = name
        self._state = self._old_state = World.STATE_LOADED
        self._tick_count = 0
        self._stats = WorldStats(name)
        self._agents = []

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):

        if new_state != self.state:
            self._old_state = self.state
            self._state = new_state

            EventQueue.add_event(Event(self._state,
                                       "Game state change from {0} to {1}".format(self._old_state, self._state),
                                       Event.STATE))

    def initialise(self, name : str = "Default World"):

        if self.state != World.STATE_LOADED:
            return

        if len(name) == 0:
            name = "Default World"

        self.state = World.STATE_INITIALISED
        self.name = name
        self._stats.initialise()
        self.load_agents()

        EventQueue.add_event(Event(World.STATE_INITIALISED,
                                   "The world of '{0}' has been created!".format(self.name),
                                   Event.STATE))

    def run(self):
        if self.state == World.STATE_LOADED:
            return

        self.pause(is_paused=False)

    def load_agents(self):
        for i in range(0,10):
            new_agent = Agent("agent {0}".format(i), "default")
            self.add_agent(new_agent)

    def add_agent(self, new_agent : Agent):
        self._agents.append(new_agent)

    def tick(self):

        if self.state != World.STATE_PLAYING:
            return

        self._tick_count += 1

        # Tick the Stat Engine
        self._stats.update_stat(WorldStats.INPUT_TICK_COUNT, self._tick_count)

        # See if any of the event stats fires as a result if the tick...
        for event_stat_name in WorldStats.EVENTS:
            stat = self._stats.get_stat(event_stat_name)
            if stat.value is True:
                EventQueue.add_event(Event(stat.name,
                                           "Event stat fired: {0}={1}".format(stat.name, stat.value),
                                           "EVENT"))

        for agent in self._agents:
            agent.tick()

        # EventQueue.add_event(Event(World.EVENT_TICK,
        #                             "World '{0}' ticked to {1}".format(self.name, self._tick_count),
        #                             World.EVENT_TICK))

    def pause(self, is_paused: bool = True):

        if self.state == World.STATE_PAUSED or is_paused is False:

            self.state = World.STATE_PLAYING

        else:
            self.state = World.STATE_PAUSED

    def end(self):

        self.state = World.STATE_DESTROYED

        EventQueue.add_event(Event(World.STATE_DESTROYED,
                                   "The world of '{0}' has ended!".format(self.name),
                                   Event.STATE))

    def print(self):

        print("\nThe world of '{0}' (state={1} tick={2}).".format(self.name,
                                                                self.state,
                                                                self._tick_count))

        self._stats.print()

        if len(self._agents) > 0:
            for agent in self._agents:
                print(str(agent))

    def get_next_event(self):

        next_event = None
        if EventQueue.size() > 0:
            next_event = EventQueue.pop_event()

        return next_event


