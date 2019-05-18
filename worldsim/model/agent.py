from .agent_stats import AgentStats

class Agent:

    def __init__(self, name : str, type : str):
        self.name = name
        self.type = type
        self._tick_count = 0
        self._stats = AgentStats(name)

    def tick(self):
        self._tick_count += 1

    def __str__(self):
        _str = "{0} (type:{1} tick:{2})".format(self.name, self.type, self._tick_count)
        return _str