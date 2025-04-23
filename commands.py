import cmd

class CommandShell(cmd.Cmd):
    main = None
    intro = "Virtual Astronaut shell initiated... Type ? to list commands.\n"
    prompt = "> "

    def do_status(self, args):
        'Print information about the server'
        print(self.main)

    def do_client(self, args):
        'Print information about the current connected client'
        if (self.main.current_client is None):
            print("No client connected!\n")
        else:
            print(f"Client address: {self.main.current_client.remote_address[0]}\n")
            print(f"Client port: {self.main.current_client.remote_address[1]}\n")
            print(f"Client UDP port: {self.main.client_udp_port}\n")

    def do_toggle(self, args : str):
        "Toggle a boolean attribute of the server"
        words = args.split(' ')
        if (len(words) < 2):
            print("Not enough arguments (hint ... attribute, value)\n")
            return
        
        self.main.toggle(words)

    def do_fake(self, args : str):
        "Sets a fake UDP client (ex: fake address port)"
        words = args.split(' ')
        if (len(words) < 2):
            print("Not enough arguments")
            return
        
        self.main.client_udp_port = int(words[1])

        class RemoteAddr:
            remote_address = None

        addr = RemoteAddr()
        addr.remote_address = (words[0], self.main.client_udp_port)

        self.main.current_client = addr

    def do_dump(self, args):
        "Print the current log history to the terminal"
        print("DUMP START ======================")
        print(self.main.logging)
        print("DUMP END ========================\n")

    def do_exit(self, args):
        "Exit the terminal and terminate the server"
        self.main.active = False
        self.main.server_task.cancel()
        return True
    
    def __init__(self, main):
        super(CommandShell, self).__init__()
        self.main = main

if __name__ == "__main__":
    print("Do not run this on its own!\n")
