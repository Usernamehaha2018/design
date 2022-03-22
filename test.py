import checker
from MCLock import Semaphore
from MCThread import MCThread

# class Mutex:
#single writer assumed
    
#     Rcount = 0  
#     Wmutex = Semaphore("WM",1)  
#     Rmutex = Semaphore("RM", 1)  
#     File = Semaphore("FILE", 1)  
#     Wirte = Semaphore("Write",1)

#     @MCThread
#     def t1(self):
#         self.Wirte.P()
#         self.Rmutex.P()
#         if self.Rcount == 0:
#             self.File.P()
#         self.Rcount += 1
#         self.Rmutex.V()
#         self.Wirte.V()
#         self.Rmutex.P()
#         self.Rcount -= 1
#         if self.Rcount == 0:
#             self.File.V()
#         self.Rmutex.V()

#     @MCThread
#     def t2(self):
#         self.Wmutex.P()
#         self.Wirte.P()
#         self.Wmutex.V()
#         self.File.P()
#         self.File.V()
#         self.Wmutex.P()
#         self.Wirte.V()
#         self.Wmutex.V()


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

checker.check()