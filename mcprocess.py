class Mutex:
    lock1 = MCLock('lk1')
    lock2 = MCLock('lk2')

    def t1(self):
        yield checkpoint()
        while True:
            yield checkpoint()
            self.lock1.acquire()
            yield checkpoint()
            self.lock2.acquire()
            yield checkpoint()
            self.lock2.release()
            yield checkpoint()
            self.lock1.release()
            yield checkpoint()
        yield checkpoint()

    def t2(self):
        yield checkpoint()
        while True:
            yield checkpoint()
            self.lock2.acquire()
            yield checkpoint()
            self.lock1.acquire()
            yield checkpoint()
            self.lock1.release()
            yield checkpoint()
            self.lock2.release()
            yield checkpoint()
        yield checkpoint()
