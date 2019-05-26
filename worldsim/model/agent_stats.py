import random

from .StatEngine import *

class Sleepiness(DerivedStat):
    NAME = "Sleepiness"
    MAX_SLEEPINESS = 100
    MIN_SLEEPINESS = 0

    def __init__(self):
        super(Sleepiness, self).__init__(Sleepiness.NAME, "AGENT")

        self.add_dependency(AgentStats.INPUT_TICK_COUNT)
        self.add_dependency(AgentStats.INPUT_CURRENT_STATE)
        self._sleepiness = 0

    def calculate(self):
        #tick_count = self.get_dependency_value(AgentStats.INPUT_TICK_COUNT)
        state = self.get_dependency_value(AgentStats.INPUT_CURRENT_STATE)

        if state == AgentStats.STATE_ASLEEP and self._sleepiness > Sleepiness.MIN_SLEEPINESS:
            self._sleepiness -= 1
        elif self._sleepiness < Sleepiness.MAX_SLEEPINESS:
            self._sleepiness += 1

        return self._sleepiness


class Hunger(DerivedStat):
    NAME = "Hunger"
    MAX_HUNGER = 100
    MIN_HUNGER = 0

    def __init__(self):
        super(Hunger, self).__init__(Hunger.NAME, "AGENT")

        self.add_dependency(AgentStats.INPUT_TICK_COUNT)
        self.add_dependency(AgentStats.INPUT_FOOD_CONSUMED)
        self._hunger = 0

    def calculate(self):
        # tick_count = self.get_dependency_value(AgentStats.INPUT_TICK_COUNT)
        food = self.get_dependency_value(AgentStats.INPUT_FOOD_CONSUMED)

        if food == 0 and self._hunger < Hunger.MAX_HUNGER:
            self._hunger += 1
        else:
            self._hunger = max(Hunger.MIN_HUNGER, self._hunger - food)

        return self._hunger


class Energy(DerivedStat):
    NAME = "Energy"
    INITIAL_ENERGY = 50
    MIN_ENERGY = 0
    MAX_ENERGY = 100

    def __init__(self):
        super(Energy, self).__init__(Energy.NAME, "AGENT")

        self.add_dependency(AgentStats.INPUT_TICK_COUNT)
        self.add_dependency(AgentStats.INPUT_ENERGY_CONSUMED)
        self.add_dependency(AgentStats.INPUT_MAX_ENERGY)
        self._energy = Energy.INITIAL_ENERGY

    def calculate(self):

        # tick_count = self.get_dependency_value(AgentStats.INPUT_TICK_COUNT)
        energy = self.get_dependency_value(AgentStats.INPUT_ENERGY_CONSUMED)
        max_energy = Energy.MAX_ENERGY

        self._energy = max(Energy.MIN_ENERGY, min(self._energy + energy - 1, max_energy))

        return self._energy


class AgentStats(StatEngine):

    # States
    STATE_DEAD = 100
    STATE_AWAKE = 1
    STATE_ASLEEP = 4

    # Input Stats
    INPUT_TICK_COUNT = "Tick Count"
    INPUT_FOOD_CONSUMED = "Food eaten"
    INPUT_CURRENT_STATE = "State"
    INPUT_MAX_ENERGY = "Maximum Energy"
    INPUT_ENERGY_CONSUMED = "Energy consumed"

    # Output Stats

    # Event stats
    EVENT_BORN = "Born"
    EVENT_DIED = "Died"

    INPUT_STATS = (INPUT_CURRENT_STATE, INPUT_TICK_COUNT, INPUT_FOOD_CONSUMED, INPUT_ENERGY_CONSUMED, INPUT_MAX_ENERGY)
    CORE_STATS = (INPUT_TICK_COUNT, INPUT_CURRENT_STATE)
    EVENT_STATS = (EVENT_BORN, EVENT_DIED)
    OUTPUT_STATS = (Energy.NAME, Sleepiness.NAME, Hunger.NAME)



    def __init__(self, name : str):
        super(AgentStats, self).__init__(name)

    def initialise(self):

        # Add the core input stats
        for core_stat_name in (AgentStats.CORE_STATS + AgentStats.INPUT_STATS):
            self.add_stat(CoreStat(core_stat_name, "INPUTS", 0))

        self.update_stat(AgentStats.INPUT_MAX_ENERGY, 100)
        self.update_stat(AgentStats.INPUT_CURRENT_STATE, AgentStats.STATE_AWAKE)

        # Add derived game stats
        self.add_stat(Hunger())
        self.add_stat(Sleepiness())
        self.add_stat(Energy())






