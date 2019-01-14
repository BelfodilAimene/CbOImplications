class Data :
    def __init__(self, alphabet, horizontal, vertical):
        self.alphabet = alphabet
        self.horizontal = horizontal
        self.vertical = vertical
        
        self.n = len(self.horizontal)
        self.m = len(self.vertical)

        # TODO : compute implications (or read implications)
        # TODO : enumeration class and how to print only useful knowledge

    @staticmethod
    def from_horizontal(alphabet, horizontal):
        return Data(alphabet, horizontal, Data._reverse_representation(horizontal))

    @staticmethod
    def from_vertical(alphabet, vertical):
        return Data(alphabet, Data._reverse_representation(vertical), vertical)
    
    @staticmethod
    def _reverse_representation(representation):
        """
        Transform a horizontal representation (list of itemsets) to a vertical representation (list of item extents) or vice-verca

           @param representation: the horizontal/vertical base
        """
        if not representation: return []
        reversed_size = max(map(max,filter(lambda e : len(e)>0, representation)))+1
        return [frozenset([i for i,elements in enumerate(representation) if element in elements]) for element in range(reversed_size)]

    def get_column_clarified_dataset(self):
        return self.fusion_equivalent_itemsets(self.get_equivalent_items())

    def fusion_equivalent_itemsets(self, equivalent_items):
        """
        @param: equivalent_items is partition of the set of items into sets of equivalent items
        it is map where the key is the first item 
        """
        new_alphabet = []
        new_vertical = []
        
        for eq_items in equivalent_items:
            new_alphabet.append("&".join(map(lambda i : self.alphabet[i], eq_items)))
            new_vertical.append(self.vertical[min(eq_items)])
        new_horizontal = Data._reverse_representation(new_vertical)

        return Data(new_alphabet, new_horizontal, new_vertical)
    
    def get_equivalent_items(self):
        # first implementation O(n^2)
        equivalent_items = []
        remaining = range(self.m)
        while remaining:
            i = remaining.pop(0)
            equivalent_to_i = [i]
            for j in list(remaining):
                if self.vertical[i] == self.vertical[j] :
                    equivalent_to_i.append(j)
                    remaining.remove(j)
            equivalent_items.append(equivalent_to_i)
        return equivalent_items

    def get_reversed_implications(self):
        """
        Return a tuple containing three elements:
           - Roots   : items that does not imply anything
           - childs  : A list containing for each i the set of j -> i (and there is no k s.t. j -> k -> i)
           - parents : A list containing for each i the set of i -> j (and there is no k s.t. i -> k -> j)
        """
        # Does work only in column-clarified datasets where there is no cycle 
        # first implementation O(n^2)
        if self.m == 0 : return [] 
        
        childs  = {i : [] for i in range(self.m)}
        childs[-1] = []

        parents = {i : [] for i in range(self.m)}
        parents[-1] = []
        
        
        root_extent = frozenset(range(self.m))
        
        for i in range(0,self.m):
            current_parent = -1
            current_parent_extent = root_extent
            current_childs = childs[current_parent]

            while len(current_childs)>0:
                parent_changed = False
                for child in childs[current_parent]:
                    if self.vertical[child].issuperset(self.vertical[i]):
                        current_parent = child
                        current_parent_extent = self.vertical[child]
                        parent_changed = True
                        break
                current_childs = childs[current_parent]
                if not parent_changed : break

            for child in list(current_childs) :
                if self.vertical[i].issuperset(self.vertical[child]):
                    parents[child].remove(current_parent)
                    parents[child].append(i)
                    
                    childs[current_parent].remove(child)
                    childs[i].append(child)
                    
            parents[i].append(current_parent)
            childs[current_parent].append(i)

        return (map(frozenset,[filter(lambda e : e != -1, childs[i]) for i in range(self.m)]),
                map(frozenset,[filter(lambda e : e != -1, parents[i]) for i in range(self.m)]))
        
        

    @staticmethod
    def read(itemsets_file):
        with open(itemsets_file):
            with open(itemsets_file, 'r') as f:
                all_lines = f.readlines()
                itemsets = map(lambda e : frozenset() if e in (" \n"," ") else frozenset(map(str,e.replace("\n","").split(" "))),all_lines)

        # compute alphabet
        alphabet = set()
        for itemset in itemsets :
            alphabet |= itemset
        alphabet = sorted(alphabet)

        # compute new itemsets where item are indices of item in alphabet
        alphabet_to_indice = {item : i for i,item in enumerate(alphabet)}
        horizontal = map(lambda e: frozenset(map(lambda item : alphabet_to_indice[item], e)), itemsets)
        vertical = Data._reverse_representation(horizontal)

        return Data(alphabet, horizontal, vertical)

    def write(self, file_path):
        with open(file_path, 'w') as the_file:
            for itemset in self.horizontal:
                the_file.write(self._str_itemset(itemset)+'\n')

    def _str_itemset(self, itemset):
        return " ".join(self.alphabet[i] for i in sorted(itemset))

    def __str__(self):
        return "\n".join([self._str_itemset(itemset) for itemset in self.horizontal])
        
