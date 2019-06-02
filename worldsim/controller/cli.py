import cmd
import worldsim.model as model
from .utils import *

class WSCLI(cmd.Cmd):
    intro = "Welcome to World Sim"
    prompt = "What next?"

    def __init__(self):

        super(WSCLI, self).__init__()

        self.model = model.World()

    def run(self):
        """Run the game"""
        self.cmdloop()

    def emptyline(self):
        pass

    def postcmd(self, stop, line):
        self.print_events()
        return cmd.Cmd.postcmd(self, stop, line)

    def do_start(self, arg):
        """Start a new world with the name specified e.g. start MyWorld"""
        args = arg.split(" ")
        self.model.initialise(args[0])
        self.model.run()

    def do_pause(self, args):
        self.model.pause(is_paused=True)

    def do_tick(self, arg):
        """Do a specified number of ticks on the world e.g. tick 5"""

        if len(arg) == 0:
            i = 1
        else:
            i = is_numeric(arg)

        if i is not None:
            for i in range (0, i):
                self.model.tick()
                #self.view.tick()


    def do_print(self, args):

        self.model.print()

    def do_eat(self, args):
        """Make a specified agent eat"""

        name = pick("Agent", self.model.get_agent_names())
        if name is not None:
            food = int(input("Food to eat?"))
            agent = self.model.get_agent(name)
            agent.eat(food)

    def do_drink(self, args):
        """Make a specified agent drink"""

        name = pick("Agent", self.model.get_agent_names())
        if name is not None:
            fluid = int(input("Fluid to drink?"))
            agent = self.model.get_agent(name)
            agent.drink(fluid)

    def do_sleep(self, args):
        """Make a selected agent go to sleep"""

        name = pick("Agent", self.model.get_agent_names())
        if name is not None:
            ticks = int(input("Amount of sleep?"))
            agent = self.model.get_agent(name)
            agent.sleep(ticks)

    def do_examine(self, args):
        """Examine a selected agent"""

        name = pick("Agent", self.model.get_agent_names())
        if name is not None:
            agent = self.model.get_agent(name)
            agent.examine()


    def do_temp(self, args):
        """Change the ambient temperature of the world"""

        new_temperature = float(input("New temperature?"))
        self.model.set_temperature(new_temperature)


    def do_quit(self, arg):
        """Quit the game"""
        try:

            if confirm("Are you sure you want to quit?") is True:
                print("\nThanks for playing.")

                self.model.end()

                print("\nBye bye.")

        except Exception as err:
            print(str(err))


    def print_events(self):

        # Print any events that got raised
        event = self.model.get_next_event()
        if event is not None:
            print("Game event(s)...")

        while event is not None:

            print(" * " + str(event))

            event = self.model.get_next_event()

