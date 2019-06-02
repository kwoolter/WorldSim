from .StatEngine import *


class CurrentYear(DerivedStat):
    NAME = "Current Year"

    DAYS_PER_YEAR = 30

    def __init__(self):
        super(CurrentYear, self).__init__(CurrentYear.NAME, "WORLD")

        self.add_dependency(WorldStats.INPUT_TICK_COUNT)

    def calculate(self):
        tick_count = self.get_dependency_value(WorldStats.INPUT_TICK_COUNT)

        return (tick_count // (CurrentYear.DAYS_PER_YEAR * DayOfYear.TICKS_PER_DAY)) + 1


class CurrentSeason(DerivedStat):
    NAME = "Current Season"

    ERROR = 0
    WINTER = 1
    SPRING = 2
    SUMMER = 3
    AUTUMN = 4

    season_number_to_name = {
        ERROR: "ERROR!!!!",
        WINTER: "Winter",
        SPRING: "Spring",
        SUMMER: "Summer",
        AUTUMN: "Autumn"
    }

    SEASONS_PER_YEAR = 4

    def __init__(self):
        super(CurrentSeason, self).__init__(CurrentSeason.NAME, "WORLD")

        self.add_dependency(DayOfYear.NAME)

    def calculate(self):
        current_day = self.get_dependency_value(DayOfYear.NAME)
        current_season = int(((current_day-1) * CurrentSeason.SEASONS_PER_YEAR) // CurrentYear.DAYS_PER_YEAR) + 1
        return current_season


class DayOfYear(DerivedStat):
    NAME = "Day of Year"

    TICKS_PER_DAY = 8

    def __init__(self):
        super(DayOfYear, self).__init__(DayOfYear.NAME, "WORLD")

        self.add_dependency(WorldStats.INPUT_TICK_COUNT)

    def calculate(self):
        tick_count = self.get_dependency_value(WorldStats.INPUT_TICK_COUNT)

        return ((tick_count) // DayOfYear.TICKS_PER_DAY % CurrentYear.DAYS_PER_YEAR) + 1


class HourOfDay(DerivedStat):
    NAME = "Hour of Day"

    def __init__(self):
        super(HourOfDay, self).__init__(HourOfDay.NAME, "WORLD")

        self.add_dependency(WorldStats.INPUT_TICK_COUNT)

    def calculate(self):
        tick_count = self.get_dependency_value(WorldStats.INPUT_TICK_COUNT)

        return (tick_count % DayOfYear.TICKS_PER_DAY) + 1


class DayChanged(DerivedStat):
    NAME = "Day Change"

    def __init__(self):
        super(DayChanged, self).__init__(DayChanged.NAME, "GAME")

        self.add_dependency(WorldStats.INPUT_TICK_COUNT)
        self.add_dependency(DayOfYear.NAME)
        self._last_day = -999

    def calculate(self):
        current_day = self.get_dependency_value(DayOfYear.NAME)
        is_changed = (current_day != self._last_day)

        self._last_day = current_day

        return is_changed

class SeasonChanged(DerivedStat):
    NAME = "Season Change"

    def __init__(self):
        super(SeasonChanged, self).__init__(SeasonChanged.NAME, "GAME")

        self.add_dependency(WorldStats.INPUT_TICK_COUNT)
        self.add_dependency(CurrentSeason.NAME)
        self._last_season = 1

    def calculate(self):
        current_season = self.get_dependency_value(CurrentSeason.NAME)
        is_changed = (current_season != self._last_season)

        self._last_season = current_season

        return is_changed


class YearChanged(DerivedStat):
    NAME = "Year Change"

    def __init__(self):
        super(YearChanged, self).__init__(YearChanged.NAME, "GAME")

        self.add_dependency(WorldStats.INPUT_TICK_COUNT)
        self.add_dependency(CurrentYear.NAME)
        self._last_year = 1

    def calculate(self):
        current_year = self.get_dependency_value(CurrentYear.NAME)
        is_changed = (current_year != self._last_year)

        self._last_year = current_year

        return is_changed


class Temperature(DerivedStat):
    NAME = "Ambient Temperature"

    SEASON_TO_MAX_TEMPERATURE = {CurrentSeason.AUTUMN : 20,
                                 CurrentSeason.SPRING : 20,
                                 CurrentSeason.SUMMER : 40,
                                 CurrentSeason.WINTER : 10}

    SEASON_TO_TEMPERATURE_RANGE = {CurrentSeason.AUTUMN : 10,
                                  CurrentSeason.SPRING : 10,
                                  CurrentSeason.SUMMER : 15,
                                  CurrentSeason.WINTER : 20}

    def __init__(self):
        super(Temperature, self).__init__(Temperature.NAME, "WORLD")

        self.add_dependency(CurrentSeason.NAME)
        self.add_dependency(HourOfDay.NAME)

    def calculate(self):

        season = self.get_dependency_value(CurrentSeason.NAME)
        hour = self.get_dependency_value(HourOfDay.NAME)

        # Get the maximum temperature for the current season
        temperature = Temperature.SEASON_TO_MAX_TEMPERATURE[season]

        #Get the range below the maximum temperature that temperatures can fall by
        temperature_range = Temperature.SEASON_TO_TEMPERATURE_RANGE[season]

        # Based on the hour of the day calculate where in the daily temperature range we should be
        # e.g. night time is coldest, midday is the hottest
        hours = DayOfYear.TICKS_PER_DAY
        temperature -= temperature_range * (abs(hour - hours/2)*2/hours)

        return temperature

class WorldStats(StatEngine):
    # World level inputs
    INPUT_TICK_COUNT = "Tick Count"

    # Season level inputs
    INPUTS = (INPUT_TICK_COUNT, INPUT_TICK_COUNT)

    # Event stats - order determines which gets fired first
    EVENTS = (DayChanged.NAME, SeasonChanged.NAME, YearChanged.NAME)

    def __init__(self, name: str):
        super(WorldStats, self).__init__(name)

    def initialise(self):
        # Add the core input stats
        for core_stat_name in WorldStats.INPUTS:
            self.add_stat(CoreStat(core_stat_name, "INPUTS", 0))

        # Add derived game stats
        self.add_stat(DayOfYear())
        self.add_stat(HourOfDay())
        self.add_stat(CurrentYear())
        self.add_stat(CurrentSeason())
        self.add_stat(DayChanged())
        self.add_stat(SeasonChanged())
        self.add_stat(YearChanged())
        self.add_stat(Temperature())
