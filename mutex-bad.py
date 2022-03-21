class Mutex:
    lock1 = Semaphore("lk1", 1)
    lock2 = Semaphore("lk2", 1)

    @MCThread
    def t1(self):
        while True:
            self.lock1.P()
            self.lock2.P()
            self.lock2.V()
            self.lock1.V()

    @MCThread
    def t2(self):
        while True:
            self.lock2.P()
            self.lock1.P()
            self.lock1.V()
            self.lock2.V()



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
