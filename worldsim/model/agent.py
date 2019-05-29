from .agent_stats import *

class Agent:

    def __init__(self, name : str, type : str):
        self.name = name
        self.type = type
        self._state = AgentStats.STATE_AWAKE
        self._tick_count = 0
        self._stats = AgentStats(name)

        self._stats.initialise()

    def tick(self):
        self._tick_count += 1
        self._stats.update_stat(AgentStats.INPUT_CURRENT_STATE, self._state)
        self._stats.update_stat(AgentStats.INPUT_TICK_COUNT, self._tick_count)
        self._state = self._stats.get_stat(NextState.NAME).value

    def eat(self, food_amount : int = 1):

        self._stats.update_stat(AgentStats.INPUT_FOOD_CONSUMED, food_amount)
        self._stats.update_stat(AgentStats.INPUT_ENERGY_GAINED, int(food_amount / 3))
        self.tick()
        self._stats.update_stat(AgentStats.INPUT_FOOD_CONSUMED, 0)
        self._stats.update_stat(AgentStats.INPUT_ENERGY_GAINED, 0)

    def sleep(self, ticks : int = 1, awaken : bool = True):

        print("Sleeping for {0} ticks...".format(ticks))

        # Set state to be asleep
        self._state = AgentStats.STATE_ASLEEP

        # Perform the number of specified ticks
        for i in range(0, ticks):
            self.tick()

        # Awaken after the sleep is flag is set
        if awaken is True:
            self._state = AgentStats.STATE_AWAKE

    def examine(self):
        print(str(self))
        self._stats.print()

    def __str__(self):
        _str = "{0} (type:{1} tick:{2} state:{3})".format(self.name,
                                                          self.type,
                                                          self._tick_count,
                                                          AgentStats.STATE_TO_STATE_NAME[self._state])
        for stat_name in AgentStats.OUTPUT_STATS:
            stat = self._stats.get_stat(stat_name)
            if stat is not None:
                _str += "\n\t{0}={1}".format(stat_name, stat.value)

        return _str