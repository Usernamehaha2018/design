class Mutex:
    lock1 = MCLock("lk1")
    lock2 = MCLock("lk2")

    @MCThread
    def t1(self):
        self.lock1.acquire()
        while True:
            pass
        # lock2.release()
        # lock1.acquire()

    @MCThread
    def t2(self):
        self.lock2.acquire()
        while True:
            pass


    # @marker
    # def mark_t1(self, state):
    #     if localvar(state, 't1', 'cs'): return 'blue'

    # @marker
    # def mark_t2(self, state):
    #     if localvar(state, 't2', 'cs'): return 'green'

    # @marker
    # def mark_both(self, state):
    #     if localvar(state, 't1', 'cs') and localvar(state, 't2', 'cs'):
    #         return 'red'
