from enumerator import Enumerator
from dataWithImplication import DataWithImplication

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
        self.parents_degrees = map(len, self.implications.parents)
        
    def _start(self, *args,**kwargs):
        self.nb_closure_computation = 1 #Computing the closure of the emptyset
        stack = [(self.bottom_itemset(), set())]
        while stack:
            cboi_tuple, forbidden = stack.pop()
            extent, itemset, leaves, addables, future_addables = cboi_tuple
            for addable in addables - forbidden :
                next_closed = self.add_and_close_in(extent, itemset, leaves, addables, future_addables, addable, forbidden)
                self.nb_closure_computation+=1
                if next_closed != None:
                    stack.append((next_closed, set(forbidden)))
                forbidden.add(addable)
            yield leaves, extent

    def __str__(self):
        return "Close-By-One-Implications"

    def bottom_itemset(self):
        itemset = set()
        extent = set(range(self.data.n))
        leaves = set()
        addables = set(self.implications.roots)
        future_addables = dict()
        for item in self.implications.roots:
            if len(self.data.vertical[item])==self.data.n :
                self.add_in(itemset, leaves, addables, future_addables, item)
        return extent,itemset, leaves, addables, future_addables

    def add_in(self, itemset, leaves, addables, future_addables, item, new_addables = set()):
        itemset.add(item)
        addables.remove(item)
        leaves.add(item)
        leaves -= self.implications.parents[item]

        for child in self.implications.childs[item]:
            ancient_value = future_addables.get(child, -1)
            if ancient_value == -1:
                parent_degrees = self.parents_degrees[child]
                
                if parent_degrees == 1:
                    addables.add(child)
                    new_addables.add(child)
                else:
                    future_addables[child] = parent_degrees - 1
            elif ancient_value == 1:
                addables.add(child)
                new_addables.add(child)
                del future_addables[child]
            else:
                future_addables[child] = ancient_value - 1

    def add_and_close_in(self, extent, itemset, leaves, addables, future_addables, item, forbidden):
        vertical = self.data.vertical
        new_extent = extent & vertical[item]
        for i in addables & forbidden:
            if vertical[i] >= new_extent : return None

        new_itemset = set(itemset)
        new_leaves = set(leaves)
        new_addables = set(addables)
        new_future_addables = dict(future_addables)

        self.add_in(new_itemset, new_leaves, new_addables, new_future_addables, item)

        addables_to_test = new_addables - forbidden

        while addables_to_test :
            i = addables_to_test.pop()
            if vertical[i] >= new_extent :
                self.add_in(new_itemset, new_leaves, new_addables, new_future_addables,i,addables_to_test)

        return new_extent, new_itemset, new_leaves, new_addables, new_future_addables
