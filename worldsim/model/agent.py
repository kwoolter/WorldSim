from .agent_stats import AgentStats

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

    def eat(self, food_amount : int = 1):

        self._stats.update_stat(AgentStats.INPUT_FOOD_CONSUMED, food_amount)
        self._stats.update_stat(AgentStats.INPUT_ENERGY_CONSUMED, int(food_amount/3))
        self.tick()
        self._stats.update_stat(AgentStats.INPUT_FOOD_CONSUMED, 0)
        self._stats.update_stat(AgentStats.INPUT_ENERGY_CONSUMED, 0)


    def sleep(self, ticks : int = 1):

        print("Sleeping for {0} ticks...".format(ticks))

        self._state = AgentStats.STATE_ASLEEP
        self._stats.print()
        for i in range(0, ticks):
            self.tick()
        self._state = AgentStats.STATE_AWAKE


    def __str__(self):
        _str = "{0} (type:{1} tick:{2} state:{3})".format(self.name, self.type, self._tick_count, self._state)
        for stat_name in AgentStats.OUTPUT_STATS:
            stat = self._stats.get_stat(stat_name)
            if stat is not None:
                _str += "\n\t{0}={1}".format(stat_name, stat.value)

        self._stats.print()

        return _str