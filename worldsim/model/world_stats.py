from .StatEngine import *


class CurrentYear(DerivedStat):
    NAME = "Current Year"

    DAYS_PER_YEAR = 30

    def __init__(self):
        super(CurrentYear, self).__init__(CurrentYear.NAME, "GAME")

        self.add_dependency(WorldStats.INPUT_TICK_COUNT)

    def calculate(self):
        tick_count = self.get_dependency_value(WorldStats.INPUT_TICK_COUNT)

        return (tick_count // (CurrentYear.DAYS_PER_YEAR * DayOfYear.TICKS_PER_DAY)) + 1


class CurrentSeason(DerivedStat):
    NAME = "Current Season"

    WINTER = 1
    GROWING = 2
    HARVESTING = 3

    season_number_to_name = {
        WINTER: "Winter",
        GROWING: "Growing",
        HARVESTING: "Harvesting"
    }

    SEASONS_PER_YEAR = 3

    def __init__(self):
        super(CurrentSeason, self).__init__(CurrentSeason.NAME, "GAME")

        self.add_dependency(DayOfYear.NAME)

    def calculate(self):
        current_day = self.get_dependency_value(DayOfYear.NAME)
        current_season = int(((current_day-1) * CurrentSeason.SEASONS_PER_YEAR) // CurrentYear.DAYS_PER_YEAR) + 1
        return current_season


class DayOfYear(DerivedStat):
    NAME = "Day of Year"

    TICKS_PER_DAY = 2

    def __init__(self):
        super(DayOfYear, self).__init__(DayOfYear.NAME, "GAME")

        self.add_dependency(WorldStats.INPUT_TICK_COUNT)

    def calculate(self):
        tick_count = self.get_dependency_value(WorldStats.INPUT_TICK_COUNT)

        return ((tick_count) // DayOfYear.TICKS_PER_DAY % CurrentYear.DAYS_PER_YEAR) + 1


class SeasonChanged(DerivedStat):
    NAME = "Season Change"

    def __init__(self):
        super(SeasonChanged, self).__init__(SeasonChanged.NAME, "GAME")

        self.add_dependency(CurrentSeason.NAME)
        self._last_season = 0

    def calculate(self):
        current_season = self.get_dependency_value(CurrentSeason.NAME)
        is_changed = (current_season != self._last_season)

        self._last_season = current_season

        return is_changed


class YearChanged(DerivedStat):
    NAME = "Year Change"

    def __init__(self):
        super(YearChanged, self).__init__(YearChanged.NAME, "GAME")

        self.add_dependency(CurrentYear.NAME)
        # self.add_dependency(WorldStats.INPUT_TICK_COUNT)
        self._last_year = 0

    def calculate(self):
        current_year = self.get_dependency_value(CurrentYear.NAME)
        is_changed = (current_year != self._last_year)

        self._last_year = current_year

        return is_changed


class WorldStats(StatEngine):
    # World level inputs
    INPUT_TICK_COUNT = "Tick Count"

    # Season level inputs
    INPUTS = (INPUT_TICK_COUNT, INPUT_TICK_COUNT)

    # Event stats
    EVENTS = (YearChanged.NAME, SeasonChanged.NAME)

    def __init__(self, name: str):
        super(WorldStats, self).__init__(name)

    def initialise(self):
        # Add the core input stats
        for core_stat_name in WorldStats.INPUTS:
            self.add_stat(CoreStat(core_stat_name, "INPUTS", 0))

        # Add derived game stats
        self.add_stat(CurrentYear())
        self.add_stat(CurrentSeason())
        self.add_stat(DayOfYear())
        self.add_stat(SeasonChanged())
        self.add_stat(YearChanged())
