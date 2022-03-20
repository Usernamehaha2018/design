class Mutex:
    lock1 = MCLock("lk1")
    lock2 = MCLock("lk2")

    @MCThread
    def t1(self):
        while True:
            self.lock1.acquire()
            self.lock2.acquire()
            self.lock2.release()
            self.lock1.release()

    @MCThread
    def t2(self):
        while True:
            self.lock2.acquire()
            self.lock1.acquire()
            self.lock1.release()
            self.lock2.release()



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
