from .utils import EventQueue
from .utils import Event
from .agent import Agent
from .agent_stats import AgentStats
from .world_stats import *
from .map import *

import math

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
        self._agents = {}
        self._map = None

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


    @property
    def year(self):
        time = self.time
        return time[CurrentYear.NAME]

    @property
    def season(self):
        time = self.time
        return time[CurrentSeason.NAME]

    @property
    def day(self):
        time = self.time
        return time[DayOfYear.NAME]

    @property
    def hour(self):
        time = self.time
        return time[HourOfDay.NAME]

    @property
    def time(self):
        time_dict = {}
        components = (HourOfDay.NAME, DayOfYear.NAME, CurrentSeason.NAME, CurrentYear.NAME)
        for component in components:
            stat = self._stats.get_stat(component)
            if stat is not None:
                time_dict[component] = stat.value
            else:
                time_dict[component] = None

        return time_dict

    @property
    def time_str(self):

        ordinal = lambda n: "%d%s" % (n, "tsnrhtdd"[(math.floor(n / 10) % 10 != 1) * (n % 10 < 4) * n % 10::4])

        time = self.time
        str = "{0} hour of the {1} day of year {3}, the season of {2}".format(ordinal(time[HourOfDay.NAME]),
                                                            ordinal(time[DayOfYear.NAME]),
                                                            CurrentSeason.season_number_to_name[time[CurrentSeason.NAME]],
                                                            time[CurrentYear.NAME]
                                                            )
        return str


    def initialise(self, name : str = "Default World"):

        if self.state != World.STATE_LOADED:
            return

        if len(name) == 0:
            name = "Default World"

        self.state = World.STATE_INITIALISED
        self.name = name
        self._stats.initialise()
        self._map = WorldMap(self.name)
        self._map.initialise()

        self.load_agents()

        EventQueue.add_event(Event(World.STATE_INITIALISED,
                                   "The world of '{0}' has been created!".format(self.name),
                                   Event.STATE))

    def run(self):
        if self.state == World.STATE_LOADED:
            return

        self.pause(is_paused=False)

    def load_agents(self):
        for i in range(0,2):
            new_agent = Agent("agent {0}".format(i), "default")
            self.add_agent(new_agent)

    def add_agent(self, new_agent : Agent):
        self._agents[new_agent.name] = new_agent

    def get_agent(self, name : str):
        if name in self._agents.keys():
            return self._agents[name]
        else:
            return None

    def get_agent_names(self):
        return list(self._agents.keys())

    def tick(self):

        if self.state != World.STATE_PLAYING:
            return

        self._tick_count += 1

        # Tick the Stat Engine
        self._stats.update_stat(WorldStats.INPUT_TICK_COUNT, self._tick_count)

        # See if any of the event stats fired as a result if the tick...
        for event_stat_name in WorldStats.EVENTS:
            stat = self._stats.get_stat(event_stat_name)
            if stat.value is True:
                EventQueue.add_event(Event(stat.name,
                                           "Event stat fired: {0}={1}".format(stat.name, stat.value),
                                           "EVENT"))

        for agent in self._agents.values():
            agent.tick()


        for agent in self._agents.values():
            # See if any of the event stats fired as a result if the tick...
            for event_stat_name in AgentStats.EVENT_STATS:
                stat = agent._stats.get_stat(event_stat_name)
                if stat is not None and stat.value is True:
                    EventQueue.add_event(Event(stat.name,
                                               "Event stat fired: {0}={1}".format(stat.name, stat.value),
                                               "EVENT"))

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

        print(self.time_str)
        self._stats.print()

        if len(self._agents) > 0:
            for agent in self._agents.values():
                print(str(agent))

    def get_next_event(self):

        next_event = None
        if EventQueue.size() > 0:
            next_event = EventQueue.pop_event()

        return next_event


