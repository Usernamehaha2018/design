import threading
from enum import Enum

class MCStates(Enum):
    RUNNING = 1
    WAITING = 2

class MCThread():
    _instance_lock = threading.Lock()
    mcthreads = {}
    threads = []
    init = 1
    class Thread():
        def __init__(self, name):
            self.name = name 
            self.state = MCStates.RUNNING
            self.lk = None
            self.lineno = 0
            self.cur_lineno = 0

    def __init__(self, *args, **argv):
        self.__current = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(MCThread, "_instance"):
            with MCThread._instance_lock:
                if not hasattr(MCThread, "_instance"):
                    MCThread._instance = object.__new__(cls)  
        try:
            if MCThread.init:
                MCThread.threads.append(args[0].__name__)
                t = MCThread.Thread(args[0].__name__)
                MCThread.mcthreads[args[0].__name__] = t
        except IndexError:
            pass
        return MCThread._instance
    
    @staticmethod
    def set_finished():
        MCThread.init = 0

    def threads_names(self):
        return MCThread.threads

    def get_current(self):
        return self.__current

    def set_current(self, current):
        self.__current = self.mcthreads[current]
        return self.__current
    
    def change_current_state(self, state, lk):
        self.__current.state = state
        self.__current.lk = lk

    def get_thread(self, name):
        return self.mcthreads[name]

    def reset(self):
        for t in self.mcthreads.values():
            t.state = MCStates.RUNNING
            t.lk = None
            t.cur_lineno = 0

    def get_true_lineno(self, no):
        if self.__current == None:  return no 
        if self.__current.state == MCStates.RUNNING:
            self.__current.cur_lineno = no
        return self.__current.cur_lineno
    
    def __try_schedule__(self):
        if self.__current.state == MCStates.RUNNING:
            return True
        elif self.__current.state == MCStates.WAITING:
            if self.__current.lk.available():
                self.__current.lk.set_state(thread = self.__current)
                self.change_current_state(MCStates.RUNNING, None)
        return False