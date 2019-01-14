from enumerator import Enumerator

class CbO(Enumerator) :
    def _start(self, *args,**kwargs):
        self.nb_closure_computation = 1 #Computing the closure of the emptyset
        for result in self.dfs(CbOItemset.bottom_itemset(self), 0):
            yield result
        
        
    def dfs(self, itemset, pos):
        for item in range(pos, self.data.m) :
            if item in itemset.itemset : continue
            next_closed = itemset.add_and_close(item)
            self.nb_closure_computation+=1
            
            if next_closed != None:
                for result in self.dfs(next_closed, item):
                    yield result
        yield itemset.itemset, itemset.extent

    def __str__(self):
        return "Close-By-One"
        
        
        



class CbOItemset:
    def __init__(self, itemset, extent, _enumerator):
        # _enumerator is the parent enumerator to access as well as the data
        self._enumerator = _enumerator
        
        # The current itemset (set)
        self.itemset = itemset

        # The extent of the itemset in the database (set)
        self.extent = extent

    def add(self, item):
        self.itemset.add(item)
        self.extent &= self._enumerator.data.vertical[item]
        return self

    def copy(self):
        return CbOItemset(set(self.itemset), set(self.extent), self._enumerator)

    def add_and_close(self, item):
        # return the closure of the current closed itemset union the new item
        #        or None if any prohibitted element is added (element before item)
        result = self.copy()
        result.add(item)

        for i in range(item):
            if i in self.itemset : continue
            if self._enumerator.data.vertical[i] >= result.extent : return None

        for i in range(item, self._enumerator.data.m) :
            if i in self.itemset : continue
            if self._enumerator.data.vertical[i] >= result.extent : result.add(i)

        return result
        

    

    @staticmethod
    def bottom_itemset(_enumerator):
        # We are always working under the hypothesis that the dataset is column-clarified (column-reduced)
        extent = set(range(_enumerator.data.n))
        itemset = set([i for i in range(_enumerator.data.m) if _enumerator.data.vertical[i] == extent])
        
        return CbOItemset(itemset, extent, _enumerator)
        
        
    def __str__(self):
        result = ""
        result += "itemset = '"+" ".join(map(str,self.itemset))+"'\n"
        result += "leaves = '"+" ".join(map(str,self.leaves))+"'\n"
        result += "addables = '"+" ".join(map(str,self.addables))+"'\n"
        result += "future_addables = '"+" ".join(map(str,self.future_addables))+"'\n"
        result += "extent = '"+" ".join(map(str,self.extent))+"'\n"
        return result        
            
