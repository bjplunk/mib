import importlib, os

class module:
    def __init__(self, name, module):
        self.name = name
        self.active = False
        self.module = module

        print("loaded module: " + name)

class modules:
    def __init__(self):
        self.mods = []

        files = []

        ls = os.listdir("modules")
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
            self.mods.append(module(f, mod))

    # invoke function for ALL modules
    def invoke_all(self, name, *args):
        for mod in self.mods:
            if hasattr(mod.module, name):
                get_attr(mod.module, name)(*args);

    # invoke function for all loaded modules
    def invoke(self, name, *args):
        for mod in self.mods:
            if mod.active == False:
                continue
            if hasattr(mod.module, name):
                get_attr(mod.module, name)(*args);

