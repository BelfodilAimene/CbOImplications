from enumerator import Enumerator
from dataWithImplication import DataWithImplication

class CbOI(Enumerator) :
    def __init__(self, dataWithImplications):
        """
        @param data: the dataset
        @param implication_from_file_path: the implication file path, if None then the implication are computed from the dataset
        """
        super(CbOI, self).__init__(dataWithImplications.data)
        self.implications = dataWithImplications
        
    def _start(self, *args,**kwargs):
        # TODO: reorder the data such that alphabet total order is a linearization of the dag order
        
        self.nb_closure_computation = 1 #Computing the closure of the emptyset
        stack = [(CbOIItemset.bottom_itemset(self), set())]
        while stack:
            itemset, forbidden = stack.pop()
            for addable in itemset.addables - forbidden :
                next_closed = itemset.add_and_close(addable, forbidden)
                self.nb_closure_computation+=1
                if next_closed != None:
                    stack.append((next_closed, set(forbidden)))
                forbidden.add(addable)
            yield itemset.leaves, itemset.extent

    def __str__(self):
        return "Close-By-One-Implications"
              
        
        
        
        



class CbOIItemset:
    def __init__(self, itemset, extent, leaves, addables, future_addables, _enumerator):
        # _enumerator is the parent enumerator to access the implication basis as well as the data
        self._enumerator = _enumerator
        
        # The current itemset (set)
        self.itemset = itemset

        # The extent of the itemset in the database (set)
        self.extent = extent

        # items that are maximal in the itemset w.r.t. dag of implications (set)
        self.leaves = leaves

        # items that are addable to the itemset in the next step:
        #   They are items not belonging to the itemset which all parents belong to the itemset
        #   (set)
        self.addables = addables


        # items that are will become addable perhaps in the next step:
        #    They are items not belonging neither to the itemset nor to addables
        #    having at least one parent in the itemset
        #    (map[addable]int)
        self.future_addables = future_addables

    def add(self, item, update_extent = True):
	self.itemset.add(item)
        if update_extent:
            self.extent &= self._enumerator.data.vertical[item]

        self.addables.remove(item)
        self.leaves.add(item)
        self.leaves -= self._enumerator.implications.parents[item]

        for child in self._enumerator.implications.childs[item]:
            ancient_value = self.future_addables.get(child, -1)
            if ancient_value == -1:
                parent_degrees = len(self._enumerator.implications.parents[child])
                
                if parent_degrees == 1:
                    self.addables.add(child)
                else:
                    self.future_addables[child] = parent_degrees
            elif ancient_value == 1:
                self.addables.add(item)
                del self.future_addables[child]
            else:
                self.future_addables[child] = ancient_value - 1

        return self

    def copy(self):
        return CbOIItemset(set(self.itemset), set(self.extent), set(self.leaves), set(self.addables), dict(self.future_addables), self._enumerator)

    def add_and_close(self, item, prohibitted = set()):
        # return the closure of the current closed itemset union the new item
        #        or None if any prohibitted element is added
        result = self.copy()
        result.add(item)

        for i in result.addables & prohibitted:
            if self._enumerator.data.vertical[i] >= result.extent : return None

        addables_to_test = result.addables - prohibitted
        while addables_to_test :
            i = addables_to_test.pop()
            if self._enumerator.data.vertical[i] >= result.extent :
                result.add(i, update_extent= False)
                addables_to_test |= result.addables

        return result
        

    

    @staticmethod
    def bottom_itemset(_enumerator):
        bottom_itemset = CbOIItemset(set(),set(range(_enumerator.data.n)), set(), set(_enumerator.implications.roots), dict(), _enumerator)

        """ If the implications are computed from the dataset and the dataset is column-clarified then this is correct 
        if len(_enumerator.roots)==1 and len(_enumerator.data.vertical[root])==_enumerator.data.n :
            bottom_itemset.add(root)
        """

        for root in _enumerator.implications.roots:
            if len(_enumerator.data.vertical[root])==_enumerator.data.n :
                bottom_itemset.add(root) 
        return bottom_itemset
        
        
    def __str__(self):
        result = ""
        result += "itemset = '"+" ".join(map(str,self.itemset))+"'\n"
        result += "leaves = '"+" ".join(map(str,self.leaves))+"'\n"
        result += "addables = '"+" ".join(map(str,self.addables))+"'\n"
        result += "future_addables = '"+" ".join(map(str,self.future_addables))+"'\n"
        result += "extent = '"+" ".join(map(str,self.extent))+"'\n"
        return result        
            
