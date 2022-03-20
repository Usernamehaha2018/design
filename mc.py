import inspect, ast, astor, copy, sys
from pathlib import Path
from enum import Enum
import threading

from graphviz import Digraph


marker_fn =  []


class MCStates(Enum):
    RUNNING = 1
    RUNNABLE = 2
    WAITING = 3

class MCThread():
    _instance_lock = threading.Lock()
    mcthreads = {}
    threads = []
    class Thread():
        def __init__(self, name):
            self.name = name 
            self.state = MCStates.RUNNING
            self.lk = None

    def __init__(self, *args, **argv):
        self.__current = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(MCThread, "_instance"):
            with MCThread._instance_lock:
                if not hasattr(MCThread, "_instance"):
                    MCThread._instance = object.__new__(cls)  
        try:
            MCThread.threads.append(args[0].__name__)
            t = MCThread.Thread(args[0].__name__)
            MCThread.mcthreads[args[0].__name__] = t
        except IndexError:
            pass
        return MCThread._instance

    def threads_names(self):
        return MCThread.threads

    def get_current(self):
        return self.__current

    def set_current(self, current):
        self.__current = self.mcthreads[current]
    
    def awake_current(self):
        self.__current.state = MCStates.RUNNING
        self.__current.lk = None

    def reset(self):
        for t in self.mcthreads.values():
            t.state = MCStates.RUNNING
            t.lk = None

    def get_thread(self, name):
        return self.mcthreads[name]



MC = MCThread()
    



class MCLock():
    def __init__(self, name):
        self.__locked = 0
        self.__name = str(name)
        self.__belong = None
    
    def __repr__(self):
        return "Lock "+ self.__name + " "+ ("unlocked" if self.__belong == None else "=> " + self.__belong.name)

    def acquire(self):
        if self.__locked == 1:
            MC.get_current().state = MCStates.WAITING
            MC.get_current().lk = self
        else:
            self.__belong = MC.get_current()
        self.__locked = 1

    def get_state(self):
        return self.__locked
    
    def set_state(self, state, thread):
        self.__locked = state
        self.__belong = thread

    def get_name(self):
        return self.__name

    def release(self):
        if not self.__locked:
            raise RuntimeError("Lock is tried to relieve while free")
        self.__locked = 0

    def __lkcopy__(self, mc):
        self.__locked = mc.get_state()
        self.__name = mc.get_name()

def marker(fn):
    '''Decorate a member function as a state marker'''
    global marker_fn
    marker_fn.append(fn)

def localvar(s, t, varname):
    '''Return local variable value of thread t in state s'''
    return s.get(t, (0, {}))[1].get(varname, None)

def checkpoint():
    '''Instrumented `yield checkpoint()` goes here'''
    f = inspect.stack()[1].frame # stack[1] is the caller of checkpoint()
    return (f.f_lineno, { k: v for k, v in f.f_locals.items() if k != 'self' })

def hack(Class):
    '''Hack Class to instrument @mc.thread functions'''
    class Instrument(ast.NodeTransformer):
        def generic_visit(self, node, in_fn=False):
            if isinstance(node, ast.FunctionDef):
                if node.name in MC.threads_names():
                    # a @mc.thread function -> instrument it
                    in_fn, node.decorator_list = True, []
                elif node.decorator_list:
                    # a decorated function like @mc.mark -> remove it
                    return None

            body = []
            for line in getattr(node, 'body', []):
                # prepend each line with `yield checkpoint()`
                if in_fn: body.append(
                    ast.Expr(ast.Yield(
                        ast.Call(func=ast.Name(checkpoint.__name__, ctx=ast.Load()),
                            args=[], keywords=[]))) )
                body.append(self.generic_visit(line, in_fn))
            node.body = body
            return node

    if not hasattr(Class, 'hacked'):
        hacked_ast = Instrument().visit(ast.parse(Class.source))
        hacked_src, vars = astor.to_source(hacked_ast), {}
        # set a breakpoint() here to see **magic happens**!
        exec(hacked_src, globals(), vars)
        Class.hacked, Class.hacked_src = vars[Class.__name__], hacked_src
    return Class

def execute(Class, trace):
    '''Execute trace (like [0,0,0,2,2,1,1,1]) on Class'''
    def attrs(obj):
        for attr in dir(obj):
            val = getattr(obj, attr)
            if not attr.startswith('__') and type(val) in [bool, int, str, list, tuple, dict, MCLock]:
                yield attr, val

    obj = hack(Class).hacked()
    for attr, val in attrs(obj):
        if type(val) == MCLock:
            tmp = MCLock("tmp")
            tmp.__lkcopy__(val)
            val = tmp
            val.set_state(0, None)
        else:
            val = copy.deepcopy(val)
        setattr(obj, attr, val)
    MC.reset()
 
    T = []
    threads = MC.threads_names()
    for t in threads:
        fn = getattr(obj, t)
        T.append(fn()) # a generator for a thread
    S = { t: T[i].__next__() for i, t in enumerate(threads) }


    while trace:
        chosen, tname, trace = trace[0], threads[trace[0]], trace[1:]
        try:
            if T[chosen]:
                MC.set_current(tname)
                current = MC.get_current()
                if current.state == MCStates.WAITING and current.lk.get_state() == 0:
                    current.lk.set_state(1, current)
                    MC.awake_current()

                if current.state == MCStates.RUNNING:
                    S[tname] = T[chosen].__next__()
        except StopIteration:
            S.pop(tname)
            T[chosen] = None

    for attr, val in attrs(obj):
        S[attr] = val
    return obj, S

class State:
    def __init__(self, Class, trace):
        self.trace = trace
        self.obj, self.state = execute(Class, trace)
        self.name = f's{abs(State.freeze(self.state).__hash__())}'

    @staticmethod
    def freeze(obj):
        '''Create an object's hashable frozen (immutable) counterpart'''
        if obj is None or type(obj) in [str, int, bool]:
            return obj
        elif type(obj) in [list, tuple]:
            return tuple(State.freeze(x) for x in obj)
        elif type(obj) in [dict]:
            return tuple(sorted(
                zip(obj.keys(), (State.freeze(v) for v in obj.values()))
            ))
        elif type(obj) in [MCLock]:
            return repr(obj)
        raise ValueError('Cannot freeze')

def serialize(Class, s0, vertices, edges):
    '''Serialize all model checking results'''
    print(f'CLASS({repr(Class.hacked_src)})')
    dot = Digraph(comment='The Test Table', format="png")

    sid = { s0.name: 0 }
    def name(s):
        if s.name not in sid: 
            sid[s.name] = len(sid)
        return repr(f's{sid[s.name]}')

    for u in vertices.values():
        mk = [f(u.obj, u.state) for f in marker_fn if f(u.obj, u.state)]
        print(f'STATE({name(u)}, {repr(u.state)}, {repr(mk)})')
        dot.node(name(u), f'STATE({name(u)}, {repr(u.state)}, {repr(mk)})')

    for u, v, chosen in edges:
        print(f'TRANS({name(u)}, {name(v)}, {repr(MC.threads_names()[chosen])})')
        dot.edge(name(u),name(v), f'{repr(MC.threads_names()[chosen])}')

    dot.view()

def check_bfs(Class):
    '''Enumerate all possible thread interleavings of @mc.thread functions'''
    s0 = State(Class, trace=[])

    # breadth-first search to find all possible thread interleavings
    queue, vertices, edges = [s0], {s0.name: s0}, []
    while queue:
        u, queue = queue[0], queue[1:]
        for chosen, _ in enumerate(MC.threads_names()):
            v = State(Class, u.trace + [chosen])
            if v.name not in vertices:
                queue.append(v)
                vertices[v.name] = v
            edges.append((u, v, chosen))

    serialize(Class, s0, vertices, edges)

src, vars = Path(sys.argv[1]).read_text(), {}

exec(src, globals(), vars)
Class = [C for C in vars.values() if type(C) == type].pop()
setattr(Class, 'source', src)
check_bfs(Class)
