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
        args = arg.split(" ")
        self.model.initialise(args[0])
        self.model.run()

    def do_pause(self, args):
        self.model.pause(is_paused=True)

    def do_run(self, args):
        self.model.run()

    def do_tick(self, arg):

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

        name = pick("Agent", self.model.get_agent_names())
        if name is not None:
            food = int(input("Food to eat?"))
            agent = self.model.get_agent(name)
            agent.eat(food)


    def do_sleep(self, args):

        name = pick("Agent", self.model.get_agent_names())
        if name is not None:
            ticks = int(input("Amount of sleep?"))
            agent = self.model.get_agent(name)
            agent.sleep(ticks)


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

