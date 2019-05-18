import random

from .StatEngine import *


class AgentStats(StatEngine):

    # Kindgom level inputs
    INPUT_TICK_COUNT = "Tick Count"

    def __init__(self, name : str):
        super(AgentStats, self).__init__(name)

    def initialise(self):
        pass
        # Add the core input stats
        # Add derived game stats

