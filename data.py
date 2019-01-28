import random, math
class Data :
    def __init__(self, alphabet, horizontal, vertical):
        self.alphabet = alphabet
        self.horizontal = horizontal
        self.vertical = vertical
        
        self.n = len(self.horizontal)
        self.m = len(self.vertical)

        # TODO : compute implications (or read implications)
        # TODO : enumeration class and how to print only useful knowledge

    def subcontext(self, object_indices, attribute_indices):
        new_horizontal = []
        new_alphabet = []
        indice_to_new_indice= {}
        for i in object_indices:
            itemset = self.horizontal[i]
            new_itemset = set()
            for item in itemset:
                if item not in attribute_indices: continue
                if item not in indice_to_new_indice:
                    indice_to_new_indice[item] = len(new_alphabet)
                    new_alphabet.append(self.alphabet[item])
                new_itemset.add(indice_to_new_indice[item])
            if new_itemset:
                new_horizontal.append(frozenset(new_itemset))
        if new_horizontal:
            return Data.from_horizontal(new_alphabet, new_horizontal)
        else:
            return Data([], [], [])

    def random_subcontext(self, percentage_objects, percentage_attributes):
        """
        Return a random subcontext of at most percentage objects, percentage attributes of the base context
         (The at most comes from the fact that empty attributes and empty objects are removed from the context)
        """
        new_n = int(math.ceil(percentage_objects*self.n))
        new_m = int(math.ceil(percentage_attributes*self.m))
        new_list_of_objects = range(self.n)
        new_list_of_attributes = range(self.m)
        random.shuffle(new_list_of_objects)
        random.shuffle(new_list_of_attributes)
        new_list_of_objects = new_list_of_objects[:new_n]
        new_list_of_attributes = new_list_of_attributes[:new_m]
        return self.subcontext(new_list_of_objects, new_list_of_attributes)
        

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

    @staticmethod
    def read(itemsets_file, separator = "\t"):
        with open(itemsets_file):
            with open(itemsets_file, 'r') as f:
                all_lines = f.readlines()
                itemsets = map(lambda e : frozenset() if e in (" \n",separator) else frozenset(map(str,e.replace("\n","").split(separator))),all_lines)

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

    def write(self, file_path, separator = "\t"):
        with open(file_path, 'w') as the_file:
            for itemset in self.horizontal:
                the_file.write(self._str_itemset(itemset, separator = separator)+'\n')

    def _str_itemset(self, itemset, separator = " "):
        return separator.join(self.alphabet[i] for i in sorted(itemset))

    def __str__(self):
        return "\n".join([self._str_itemset(itemset, separator = " ") for itemset in self.horizontal])
        
