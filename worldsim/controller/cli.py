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

    def do_start(self, arg):
        args = arg.split(" ")
        self.model.initialise(args[0])
        self.print_events()

    def do_tick(self, arg : str = "1"):

        i = is_numeric(arg)
        if i is not None:
            for i in range (0, i):
                self.model.tick()
                #self.view.tick()

        self.print_events()


    def do_quit(self, arg):
        """Quit the game"""
        try:

            if confirm("Are you sure you want to quit?") is True:
                print("\nThanks for playing.")

                self.model.end()
                self.print_events()

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

