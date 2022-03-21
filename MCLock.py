import inspect
class MCLock():
    def __init__(self, name, MC=None):
        self.__locked = 0
        self.__name = str(name)
        self.__belong = None
        self.__MC = MC
    
    def __repr__(self):
        return "Lock "+ self.__name + " "+ ("unlocked" if self.__belong == None \
            else "=> " + self.__belong.name)
    
    def get_name(self):
        return self.__name

    def acquire(self):
        from checker import MCStates
        assert self.__MC != None
        if self.__locked:
            self.__MC.change_current_state(MCStates.WAITING, self)
        else:
            self.__belong = self.__MC.get_current()
        self.__locked = True

    def release(self):
        if not self.__locked:
            raise RuntimeError("Lock is tried to relieve while free")
        self.__locked = False
        self.__belong = None

    def get_state(self):
        return self.__locked
    
    def set_state(self, state=True, thread=None):
        if isinstance(state, bool):
            self.__locked = state
            self.__belong = thread
        elif not thread:
            self.__locked = state
        else:
            raise ValueError("type of lock state should be bool and type of \
                thread should be MCThread, while get {} and {}"\
                .format(type(state), type(thread))) 
            
    def available(self):
        return self.__locked == False
            
class Semaphore(MCLock):
    def __init__(self, name, count, MC=None):
        super().__init__(name, MC)
        self.max_count = count
        self.__count = count
        
    def P(self):
        if self.__count > 0:
            self.__count -= 1
        else:
            super().set_state(True)
            self.acquire()
            
    def V(self):
        if self.__count < self.max_count:
            self.__count += 1
        else:
            raise ValueError("lock exceed max_count")
        
    def available(self):
        return self.__count > 0
    
    def set_state(self, thread = None):
        assert self.__count > 0
        self.__count -= 1
        
        
        
        
    
        