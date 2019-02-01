from enumerator import Enumerator

class CbO(Enumerator) :
    def _start(self, *args,**kwargs):
        self.nb_closure_computation = 1 #Computing the closure of the emptyset
        vertical = self.data.vertical
        m = self.data.m
        n = self.data.n
        
        stack = [(set(range(n)), set([item for item in range(m) if len(vertical[item]) == n]),  0)]
        while stack :
            extent, itemset, pos = stack.pop()
            for item in xrange(pos, m) :
                if item in itemset : continue

                new_extent = extent & vertical[item]
                self.nb_closure_computation+=1

                canonicity_test_fail = False
                for i in xrange(item):
                    if i in itemset : continue
                    if vertical[i] >= new_extent :
                        canonicity_test_fail = True
                        break
                if canonicity_test_fail: continue

                new_itemset = set(itemset)
                new_itemset.add(item)
                for i in xrange(item+1, m) :
                    if i in itemset : continue
                    if vertical[i] >= new_extent : new_itemset.add(i)
                
                stack.append((new_extent,new_itemset, item+1))
            yield itemset, extent
            
    def __str__(self):
        return "Close-By-One"
