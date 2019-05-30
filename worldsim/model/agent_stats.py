from .StatEngine import *


class Age(DerivedStat):
    NAME = "Age"

    def __init__(self):
        super(Age, self).__init__(Age.NAME, "AGENT")

        self.add_dependency(AgentStats.INPUT_TICK_COUNT)
        self._age = 0

    def calculate(self):
        self._age += 1

        return self._age


class Sleepiness(DerivedStat):
    NAME = "Sleepiness"
    MAX_SLEEPINESS = 100
    MIN_SLEEPINESS = 0
    ENERGY_LEVEL_THRESHOLD = 20

    def __init__(self):
        super(Sleepiness, self).__init__(Sleepiness.NAME, "AGENT")

        self.add_dependency(AgentStats.INPUT_TICK_COUNT)
        self.add_dependency(AgentStats.INPUT_CURRENT_STATE)
        self.add_dependency(Energy.NAME)
        self._sleepiness = 0

    def calculate(self):

        state = self.get_dependency_value(AgentStats.INPUT_CURRENT_STATE)
        energy = self.get_dependency_value(Energy.NAME)

        if state == AgentStats.STATE_ASLEEP and self._sleepiness > Sleepiness.MIN_SLEEPINESS:
            self._sleepiness -= 1

            if energy <= Sleepiness.ENERGY_LEVEL_THRESHOLD:
                sleep_delta = 3
            else:
                sleep_delta = 1

            self._sleepiness -= sleep_delta

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

        food = self.get_dependency_value(AgentStats.INPUT_FOOD_CONSUMED)

        if food == 0 and self._hunger < Hunger.MAX_HUNGER:
            self._hunger += 1
        else:
            self._hunger = max(Hunger.MIN_HUNGER, self._hunger - food)

        return self._hunger


class Thirst(DerivedStat):
    NAME = "Thirst"
    MAX_THIRST = 100
    MIN_THIRST = 0

    def __init__(self):
        super(Thirst, self).__init__(Thirst.NAME, "AGENT")

        self.add_dependency(AgentStats.INPUT_TICK_COUNT)
        self.add_dependency(AgentStats.INPUT_FLUID_CONSUMED)
        self._thirst = 0

    def calculate(self):

        fluid = self.get_dependency_value(AgentStats.INPUT_FLUID_CONSUMED)

        if fluid == 0 and self._thirst < Thirst.MAX_THIRST:
            self._thirst += 1
        else:
            self._thirst = max(Thirst.MIN_THIRST, self._thirst - fluid)

        return self._thirst


class Energy(DerivedStat):
    NAME = "Energy"
    INITIAL_ENERGY = 50
    MIN_ENERGY = 0
    MAX_ENERGY = 200
    SLEEP_ENERGY_REDUCTION_FACTOR = 0.3

    def __init__(self):
        super(Energy, self).__init__(Energy.NAME, "AGENT")

        self.add_dependency(AgentStats.INPUT_TICK_COUNT)
        self.add_dependency(AgentStats.INPUT_ENERGY_GAINED)
        self.add_dependency(AgentStats.INPUT_CURRENT_STATE)
        self.add_dependency(AgentStats.INPUT_MAX_ENERGY)
        self.add_dependency(Hunger.NAME)
        self._energy = Energy.INITIAL_ENERGY

    def calculate(self):

        state = self.get_dependency_value(AgentStats.INPUT_CURRENT_STATE)
        energy = self.get_dependency_value(AgentStats.INPUT_ENERGY_GAINED)
        hunger = self.get_dependency_value(Hunger.NAME)
        max_energy = Energy.MAX_ENERGY

        # The more hungry you are the more energy you consume
        energy_delta = 1
        if hunger > 30:
            energy_delta = 2
        elif hunger > 60:
            energy_delta = 3

        # If you are asleep then only use a fraction of energy
        if state == AgentStats.STATE_ASLEEP:
            energy_delta *= Energy.SLEEP_ENERGY_REDUCTION_FACTOR

        self._energy = max(Energy.MIN_ENERGY, min(self._energy + energy - energy_delta, max_energy))

        return self._energy


class ChangeState(DerivedStat):
    NAME = "Change State"

    SLEEP_THRESHOLD = 80
    STARVATION_THRESHOLD = 100
    ENERGY_THRESHOLD = 100

    def __init__(self):
        super(ChangeState, self).__init__(ChangeState.NAME, "AGENT")

        self.add_dependency(AgentStats.INPUT_CURRENT_STATE)
        self.add_dependency(AgentStats.INPUT_TICK_COUNT)

        self._current_state = AgentStats.STATE_AWAKE

    def calculate(self):
        current_state = self.get_dependency_value(AgentStats.INPUT_CURRENT_STATE)

        is_changed = False

        if self._current_state != current_state:
            is_changed = True

        self._current_state = current_state

        return is_changed


class NextState(DerivedStat):
    NAME = "Next State"

    SLEEP_THRESHOLD = 80
    STARVATION_THRESHOLD = 100
    ENERGY_THRESHOLD = 100

    def __init__(self):
        super(NextState, self).__init__(NextState.NAME, "AGENT")

        self.add_dependency(AgentStats.INPUT_CURRENT_STATE)
        self.add_dependency(Sleepiness.NAME)
        self.add_dependency(Energy.NAME)
        self.add_dependency(Hunger.NAME)
        self.add_dependency(Age.NAME)
        self.add_dependency(AgentStats.INPUT_MAX_AGE)

    def calculate(self):

        current_state = self.get_dependency_value(AgentStats.INPUT_CURRENT_STATE)
        sleepiness = self.get_dependency_value(Sleepiness.NAME)
        hunger = self.get_dependency_value(Hunger.NAME)
        energy = self.get_dependency_value(Energy.NAME)
        age = self.get_dependency_value(Age.NAME)
        max_age = self.get_dependency_value(AgentStats.INPUT_MAX_AGE)
        new_state = current_state

        if hunger >= NextState.STARVATION_THRESHOLD or energy <= 0 or age > max_age:
            new_state = AgentStats.STATE_DEAD
        elif sleepiness >= NextState.SLEEP_THRESHOLD:
            new_state = AgentStats.STATE_ASLEEP
        elif sleepiness <= Sleepiness.MIN_SLEEPINESS:
            new_state = AgentStats.STATE_AWAKE

        return new_state


class AgentStats(StatEngine):
    # States
    STATE_DEAD = 100
    STATE_AWAKE = 1
    STATE_ASLEEP = 4

    # Input Stats
    INPUT_TICK_COUNT = "Tick Count"
    INPUT_FOOD_CONSUMED = "Food eaten"
    INPUT_FLUID_CONSUMED = "Fluid consumed"
    INPUT_CURRENT_STATE = "State"
    INPUT_MAX_ENERGY = "Maximum Energy"
    INPUT_MAX_AGE = "Maximum Age"
    INPUT_ENERGY_GAINED = "Energy consumed"

    # Core Stats
    STAT_STRENGTH = "Strength"
    STAT_INTELLIGENCE = "Intelligence"

    # Output Stats

    # Event stats
    EVENT_BORN = "Born"
    EVENT_DIED = "Died"
    EVENT_FELL_ASLEEP = "Fell Asleep"

    INPUT_STATS = (INPUT_CURRENT_STATE, INPUT_TICK_COUNT, INPUT_FOOD_CONSUMED, INPUT_FLUID_CONSUMED,
                   INPUT_ENERGY_GAINED, INPUT_MAX_ENERGY, INPUT_MAX_AGE)
    CORE_STATS = (INPUT_TICK_COUNT, INPUT_CURRENT_STATE, STAT_STRENGTH, STAT_INTELLIGENCE)
    EVENT_STATS = (ChangeState.NAME, EVENT_BORN, EVENT_DIED, EVENT_FELL_ASLEEP)
    OUTPUT_STATS = (Age.NAME, Energy.NAME, Sleepiness.NAME, Hunger.NAME, Thirst.NAME)

    STATE_TO_STATE_NAME = {STATE_ASLEEP: "Asleep", STATE_AWAKE: "Awake", STATE_DEAD: "Dead"}

    def __init__(self, name: str):
        super(AgentStats, self).__init__(name)

    def initialise(self):

        # Add the base and input stats
        for core_stat_name in (AgentStats.CORE_STATS):
            self.add_stat(CoreStat(core_stat_name, "BASE STATS", 0))

        for core_stat_name in (AgentStats.INPUT_STATS):
            self.add_stat(CoreStat(core_stat_name, "INPUTS", 0))

        self.update_stat(AgentStats.INPUT_MAX_ENERGY, 100)
        self.update_stat(AgentStats.INPUT_MAX_AGE, 20)
        self.update_stat(AgentStats.INPUT_CURRENT_STATE, AgentStats.STATE_AWAKE)

        # Add derived game stats
        self.add_stat(Age())
        self.add_stat(Energy())
        self.add_stat(Hunger())
        self.add_stat(Thirst())
        self.add_stat(Sleepiness())
        self.add_stat(NextState())
        self.add_stat(ChangeState())
