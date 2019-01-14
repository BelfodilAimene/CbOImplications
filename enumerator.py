import numpy as np
import time,datetime
from random import randint
import abc
from utils import current_time_in_millis

class Enumerator :
    __metaclass__ = abc.ABCMeta
    """
    This class simulates an enumerator of closed itemsets.
    """
    def __init__(self, data):
        self.data = data

    @abc.abstractmethod
    def _start(self, *args,**kwargs):
        # Start need to be an iterator that return itemsets, extents tuples 
        return

    def start(self, verbose = False, *args,**kwargs):
        self.verbose=verbose
        self.nb_closure_computation = 0
        self.nb_closed = 0
        
        t1 = current_time_in_millis()
        for itemset, extent in self._start(*args,**kwargs):
            self.nb_closed += 1
            if (self.nb_closed%10000 == 0): print self.nb_closed 
            if self.verbose:
                print self.data._str_itemset(itemset)+":\n  extent = "+" ".join(map(str,extent))
        t2 = current_time_in_millis()
        print self
        print "  Elapsed time:                ",(t2-t1),"ms"
        print "  Nb closed:                   ",self.nb_closed,"closed itemsets"
        print "  Nb generated closed patterns:",self.nb_closure_computation,"closed itemsets"
        print ""
