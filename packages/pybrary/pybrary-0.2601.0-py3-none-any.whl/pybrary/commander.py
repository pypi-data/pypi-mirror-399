from inspect import signature, getmembers, isfunction, isclass, ismodule
from sys import argv
from textwrap import indent
from traceback import format_exc


def find_classes(*targets):
    found = []
    for target in targets:
        if isclass(target):
            found.append(target)
        elif ismodule(target):
            for name, Klass in getmembers(target, isclass):
                if hasattr(Klass, 'cmd'):
                    found.append(Klass)
        else:
            raise ValueError(f'Invalid Target ! {target}')
    return found


def find_cmds(target):
    cmds = {
        name.partition('_')[2] : cmd
        for name, cmd in getmembers(target, isfunction)
        if name.startswith('cmd_')
    }
    return cmds


class BaseCommander:
    def parse_cmds(self, target):
        self.cmds = find_cmds(target)

    def parse_args(self, *args):
        if len(args) == 1 : args = args[0].split()
        self.args = [a for a in args if '=' not in a]
        self.kwargs = dict(kv.split('=') for kv in args if '=' in kv)

    def parse(self):
        self.cmd = argv[0].split('/')[-1]
        self.action = argv[1]
        args = argv[2:]
        self.parse_args(*args)

    def get_docs(self, kv):
        spc = '\n' + ' ' * 8
        docs = {}
        for name, action in kv.items():
            if doc := action.__doc__:
                docs[name] = doc.split('\n')[0]
            else:
                docs[name] = ''
        size = max(len(k) for k in kv)
        docs_list = [
            f'{name:>{size}} : {docs[name]}'
            for name in kv
        ]
        return docs_list

    def trace(self, action, exc):
        doc = indent(action.__doc__ or '! no doc', '    ')
        sig = f'{action.__name__}{signature(action)}:'
        print(f'\n{sig}\n{doc}\n\n{exc}\n')
        with open('traceback.log', 'w') as out:
            out.write(f'{sig}\n')
            out.write(f'{doc}\n')
            out.write(f'{exc}\n')

    def get_action(self):
        target = self.target()
        action = getattr(target, f'cmd_{self.action}')
        return action

    def __call__(self):
        try:
            self.parse()
        except Exception:
            print(self.usage)
            return
        if self.action not in self.cmds:
            print(self.usage)
            return
        action = self.get_action()
        try:
            action(*self.args, **self.kwargs)
        except Exception:
            self.trace(action, format_exc())

    @property
    def usage(self):
        spc = '\n' + ' ' * 12
        usage = f'''
        {self.cmd} [action] [*args] [**kwargs]

        actions:
            {spc.join(self.get_docs(self.cmds))}
        '''
        return usage


class MonoCommander(BaseCommander):
    def __init__(self, target):
        self.target = target
        self.parse_cmds(target)


class MultiCommander(BaseCommander):
    def __init__(self, *targets):
        self.targets = {
            target.cmd : target
            for target in targets
        }
        self.parse_cmds(targets[0])

    def parse(self):
        self.cmd = argv[0].split('/')[-1]
        target = argv[1]
        self.target = self.targets[target]
        self.action = argv[2]
        args = argv[3:]
        self.parse_args(*args)

    @property
    def usage(self):
        spc = '\n' + ' ' * 12
        usage = f'''
        {self.cmd} [target] [action] [*args] [**kwargs]

        targets:
            {spc.join(self.get_docs(self.targets))}

        actions:
            {spc.join(self.get_docs(self.cmds))}
        '''
        return usage


class DictCommander(BaseCommander):
    def __init__(self, **commands):
        self.cmds = commands

    def get_action(self):
        return self.cmds[self.action]


def commander(*targets, **commands):
    if commands:
        return DictCommander(**commands)()

    if targets:
        classes = find_classes(*targets)
        spec = find_cmds(classes[0])
        if len(classes) == 1:
            if spec:
                return MonoCommander(classes[0])()
            else:
                print(f' ! no cmd in target : {classes[0]}')
        else:
            ok = True
            for Klass in classes:
                cmds = find_cmds(Klass)
                diff = spec.keys() ^ cmds.keys()
                if diff:
                    print(f' ! incompatible target : {Klass.__name__}')
                    for key in diff:
                        if key not in cmds:
                            print(f'\t Cmd not found : cmd_{key}')
                        if key not in spec:
                            print(f'\t Invalid Cmd : cmd_{key}')
                    ok = False
            if ok:
                return MultiCommander(*classes)()

    # pyproject.scripts calls without args
    return 0
