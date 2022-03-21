class Mutex:
    lock1 = Semaphore('lk1', 1)
    lock2 = Semaphore('lk2', 1)

    def t1(self):
        yield checkpoint()
        while True:
            yield checkpoint()
            self.lock1.P()
            yield checkpoint()
            self.lock2.P()
            yield checkpoint()
            self.lock2.V()
            yield checkpoint()
            self.lock1.V()
            yield checkpoint()
        yield checkpoint()

    def t2(self):
        yield checkpoint()
        while True:
            yield checkpoint()
            self.lock2.P()
            yield checkpoint()
            self.lock1.P()
            yield checkpoint()
            self.lock1.V()
            yield checkpoint()
            self.lock2.V()
            yield checkpoint()
        yield checkpoint()
