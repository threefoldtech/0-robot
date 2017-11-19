from js9 import j
from JumpScale9.tools.zerorobot.ZeroTemplates import *
class Template(ZeroTemplate):

    def init(self):    
        self.version=1.0


    @retry
    @our_decorator
    def start(self):
        time.sleep(1)
        raise RuntimeError("D")

    def stop(self):
        pass

    def restart(self):
        self.stop()
        self.start()


    def monitor(self):
        """

        config='''
        recurring : 60
        log : False
        job : False
        timeout_policy : "mypolicy1"
        '''

        """
        pass