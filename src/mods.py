import importlib, os, sys

class module:
    def __init__(self, irc, name, module):
        print("Loading module: " + name)
        self.irc = irc
        self.name = name
        self.active = False
        self.module = module

        self.call_func('init', irc)

        if hasattr(module, 'get_commands'):
            self.commands = module.get_commands() # get a list of commands the module registers
        else:
            self.commands = []

        if module.active_by_default:
            self._active_toggle(True)

    def call_func(self, name, *args):
        if hasattr(self.module, name):
            getattr(self.module, name)(*args)

    def activate(self):
        if self.active:
            return
        self._active_toggle(True)

    def deactivate(self):
        if not self.active:
            return
        self._active_toggle(False)

    def _active_toggle(self, on):
        if on:
            for cmd in self.commands:
                args = cmd['args'] if 'args' in cmd else []
                optargs = cmd['optargs'] if 'optargs' in cmd else []
                help = cmd['help'] if 'help' in cmd else ""
                self.irc.commands.register_cmd(cmd['name'], cmd['type'], cmd['priv'], cmd['func'], args, optargs, help)
            self.call_func('activate')
            self.active = True
        else:
            for cmd in self.commands:
                self.irc.commands.unregister_cmd(cmd.name)
            self.call_func('deactivate')
            self.active = False

class modules:
    def __init__(self, irc):
        self.mods = []
        self.irc = irc

        files = []

        try:
            ls = os.listdir("modules")
        except OSError:
            try:
                ls = os.listdir("src/modules")
            except:
                sys.exit("Could not find modules directory.")

        for f in ls:
            if f.startswith(".") or f.startswith("_"):
                continue
            try:
                name, ext = f.split(os.extsep, 1)
            except ValueError:
                continue
            if ext != "py":
                continue

            files.append(name)

        for f in files:
            mod = getattr(__import__("modules." + f), f)
            self.mods.append(module(self.irc, f, mod))

    def get_module(self, name):
        for mod in self.mods:
            if mod.name == name:
                return mod
        return None

    # invoke function for ALL modules
    def invoke_all(self, name, *args):
        for mod in self.mods:
            mod.call_func(name, *args)

    # invoke function for all loaded modules
    def invoke(self, name, *args):
        for mod in self.mods:
            if mod.active == False:
                continue
            mod.call_func(name, *args)

