from tarjan import tarjan
from data import Data
import math, random

import networkx as nx
import matplotlib.pyplot as plt


class DataWithImplication:
    def __init__(self, data, childs, parents):
        """
        the real implications can be took from parents
        """
        self.data = data
        self.childs = childs
        self.parents = parents
        self.roots = frozenset([i for i,parent in enumerate(self.parents) if len(parent)==0])

        self.nb_implications = sum(map(len, self.parents))

    def strict_implication_relation_size(self):
        return sum(map(lambda i : len(self.get_filter(i)), range(self.data.m)))-self.data.m

    def strict_total_implication_relation_size(self):
        return sum(map(lambda i: len(DataWithImplication.get_real_filter(self.data,i)), range(self.data.m)))-self.data.m  

    def knowledge_density(self):
        total = self.strict_total_implication_relation_size()
        if total == 0 : return 1.
        return float(self.strict_implication_relation_size())/self.strict_total_implication_relation_size()
                
            
        
    """
    Subsampling
    """
    def subdataset(self, object_indices, attribute_indices):
        new_horizontal = []
        new_alphabet = []
        old_indice_to_new_indice= {}
        
        
        for i in object_indices:
            itemset = self.data.horizontal[i]
            new_itemset = set()
            for item in itemset:
                if item not in attribute_indices: continue
                if item not in old_indice_to_new_indice:
                    old_indice_to_new_indice[item] = len(new_alphabet)
                    new_alphabet.append(self.data.alphabet[item])
                new_itemset.add(old_indice_to_new_indice[item])
            if new_itemset:
                new_horizontal.append(frozenset(new_itemset))
        if not new_horizontal:
            return DataWithImplications.no_implications(Data([], [], []))

        new_data = Data.from_horizontal(new_alphabet, new_horizontal)

        new_indice_to_old_indice = [None for i in range(len(new_alphabet))]
        for k,v in old_indice_to_new_indice.iteritems():
            new_indice_to_old_indice[v] = k

        new_parents = []
        for old_indice in new_indice_to_old_indice:
            new_parent = set()
            for old_parent in self.parents[old_indice]:
                if old_parent in old_indice_to_new_indice:
                    new_parent.add(old_indice_to_new_indice[old_parent])
            new_parents.append(frozenset(new_parent))

        new_childs = DataWithImplication.reverse(new_parents)
          
        
        return DataWithImplication(new_data, new_childs, new_parents)

    def subimplications(self, implications_to_keep):
        new_parents = [set() for _ in range(self.data.m)]
        i = 0
        for indice, parent in enumerate(self.parents):
            for p in parent:
                if i in implications_to_keep:
                    new_parents[indice].add(p)
                i+=1
        new_data = Data(list(self.data.alphabet), list(self.data.horizontal), list(self.data.vertical))
        new_parents = map(frozenset, new_parents)
        new_childs = DataWithImplication.reverse(new_parents)
        return DataWithImplication(new_data, new_childs, new_parents)

    def random_subdataset(self, percentage_objects, percentage_attributes):
        new_n = int(math.ceil(percentage_objects*self.data.n))
        new_m = int(math.ceil(percentage_attributes*self.data.m))
        
        new_list_of_objects = range(self.data.n)
        new_list_of_attributes = range(self.data.m)
        
        random.shuffle(new_list_of_objects)
        random.shuffle(new_list_of_attributes)
        
        new_list_of_objects = sorted(new_list_of_objects[:new_n])
        new_list_of_attributes = sorted(new_list_of_attributes[:new_m])
        
        return self.subdataset(new_list_of_objects,new_list_of_attributes)

    def random_subimplications(self, percentage_implications):
        new_nb_implications = int(math.ceil(percentage_implications*self.nb_implications))
        
        new_list_of_implications_indices = range(self.nb_implications)
        
        random.shuffle(new_list_of_implications_indices)
        
        new_list_of_implications_indices = sorted(new_list_of_implications_indices[:new_nb_implications])
        
        return self.subimplications(new_list_of_implications_indices)

    def random_subimplications_list(self, percentages_implications):
        """
        return list of data with subsampled implications
        """
        shuffeled_implications = range(self.nb_implications)
        random.shuffle(shuffeled_implications)
        return [self.subimplications(sorted(shuffeled_implications[:int(math.ceil(p*self.nb_implications))])) for p in sorted(percentages_implications)]

    def random_subdataset_and_subimplications(self, percentage_objects, percentage_attributes, percentage_implications):
        return self.random_subdataset(percentage_objects, percentage_attributes).random_subimplications(percentage_implications)
    """
    -----------------------------------------------
    """


    @staticmethod
    def from_data(data, implication_file_path = None, compute_implications = True, separator = "\t"):
        if implication_file_path == None:
            if compute_implications:
                return DataWithImplication.compute_implications(data)
            else:
                return DataWithImplication.no_implications(data)
        else :
            return DataWithImplication.read_implications(data, implication_file_path, separator = separator)

    

    @staticmethod
    def read_implications(data, implication_file_path, separator = "\t"):
        parents = DataWithImplication.read_implications_file(data, implication_file_path, separator = separator)
        childs = DataWithImplication.reverse(parents)
        return DataWithImplication(data,childs,parents)

    @staticmethod
    def compute_implications(data):
        parents = [DataWithImplication.get_real_filter(data, i)-frozenset([i]) for i in range(data.m)]
        childs = DataWithImplication.reverse(parents)
        
        return DataWithImplication(data,childs,parents)

    def reduct(self):
        if self.nb_implications == 0 :
            return self
        implications = list(self.parents)
        data = self.data
        
        equivalent_items = tarjan({i:childs for i,childs in enumerate(implications)})
        equivalent_items = sorted(map(sorted,equivalent_items), key=lambda element: element[0])
        old_to_new_indice = [None for i in range(data.m)]
        for new_indice, equivalents in  enumerate(equivalent_items):
            for old_indice in equivalents:
                old_to_new_indice[old_indice] = new_indice
        new_implications = []

        for element in equivalent_items :
            new_childs = set()
            for i in element :
                new_childs |= set(map(lambda old : old_to_new_indice[old],implications[i]))
            new_implications.append(frozenset(new_childs)-frozenset([len(new_implications)]))

        semi_reduced_data = data.fusion_equivalent_itemsets(equivalent_items)

        parents = DataWithImplication._remove_indirect_implications(new_implications)
        childs = DataWithImplication.reverse(parents)
        return DataWithImplication(semi_reduced_data, childs, parents)

    @staticmethod
    def read_implications_file(data, from_file, separator = "\t", check = False):
        """
        return one list of sets:
            for the set of position i the sets regroups implications which premises is item i
        """
        symbol_to_indice = {symbol:i for i,symbol in enumerate(data.alphabet)}
        
        base_implications = []

        result = [set() for i in range(data.m)]
        
        with open(from_file):
            with open(from_file, 'r') as f:
                all_lines = f.readlines()
                for line in all_lines:
                    implication = line.strip().replace("\n", "").split(separator)
                    if len(implication) != 2:
                        raise Exception("Implication need to be of the form 'a b'")
                    if implication[0] not in symbol_to_indice or implication[1] not in symbol_to_indice:
                        raise Exception("Symbols needs to belong to the dataset alphabet")
                    if implication[0]==implication[1] :
                        continue
                    
                    result[symbol_to_indice[implication[0]]].add(symbol_to_indice[implication[1]])

                implications = map(frozenset,result)
                if not check or DataWithImplication.check_implications(data, implications):
                    return implications

    @staticmethod
    def check_implications(data, implications):
        for i, implied in enumerate(implications):
            for j in implied :
                set_of_counter_examples = data.vertical[i] - data.vertical[j]
                if len(set_of_counter_examples) > 0:
                    raise Exception("item '"+data.alphabet[i]+"' does not imply item '"+data.alphabet[j]+
                                    "'. Indeed objects "+",".join(map(str, set_of_counter_examples))+
                                    " have item '"+data.alphabet[i]+
                                    "' but do not have '"+data.alphabet[j]+"'")
        return True

    def sorted_alphabet_dataset_with_implications(self):
        """
        return a dataset which alphabet is sorted in such a way that the order
        is a linearization of the partial order of implications set
        """
        # Finding a linearization -------------------------------------
        # TODO: Optimize this computations 
        new_order = []
        
        potential_addables = set()

        addables = set(self.roots)
        potential_addables = set()
        
        while addables:
            element = min(addables)
            new_order.append(element)
            potential_addables|=set([child for child in self.childs[element] if child not in new_order])
            addables.remove(element)
            for i in set(potential_addables):
                if all([parent in new_order for parent in self.parents[i]]):
                    potential_addables.remove(i)
                    addables.add(i)
        # -------------------------------------------------------------

        # Correcting the indices  -------------------------------------
        old_to_new = list(new_order)
        for old_indice, new_indice in enumerate(new_order):
            old_to_new[old_indice] = new_indice
            
        new_alphabet = [self.data.alphabet[i] for i in new_order]
        new_vertical = [self.data.vertical[i] for i in new_order]
        new_data = Data.from_vertical(new_alphabet, new_vertical)
        new_childs = map(lambda item_childs : map(lambda i: old_to_new[i], item_childs) ,self.childs)
        new_childs = [frozenset(new_childs[i]) for i in new_order]
        # -------------------------------------------------------------

        return DataWithImplication(new_data,new_childs,DataWithImplication.reverse(new_childs))

    

    @staticmethod
    def _remove_indirect_implications(parents):
        all_strict_filters = [DataWithImplication._get_filter(parents,i)-set([i]) for i in range(len(parents))]
        new_parents = []
        for i,i_parents in enumerate(parents):
            new_i_parents = set(i_parents)-set([i])
            for j in i_parents:
                new_i_parents-=all_strict_filters[j]
            new_parents.append(new_i_parents)
        return parents

    @staticmethod
    def no_implications(data):
        childs = [frozenset() for i in range(data.m)]
        parents = [frozenset() for i in range(data.m)]
        return DataWithImplication(data,childs,parents)

    @staticmethod
    def read(data_file_path, implication_file_path = None, compute_implications = True, separator = "\t"):
        """
        @param data_file_path : itemset file path
        @param implication_file_path: implications file path
        @param compute_implications: if implication_file_path is None wether or note compute the set of implication using the dataset
        """
        data = Data.read(data_file_path, separator = separator)
        return DataWithImplication.from_data(data, implication_file_path, compute_implications, separator = separator)

    @staticmethod
    def read_and_reduct(data_file_path, implication_file_path = None, compute_implications = True, separator = "\t"):
        """
        @param data_file_path : itemset file path
        @param implication_file_path: implications file path
        @param compute_implications: if implication_file_path is None wether or note compute the set of implication using the dataset
        """
        return DataWithImplication.read(data_file_path, implication_file_path, compute_implications, separator).reduct()

    def write(self, data_file_path, implication_file_path, separator = "\t"):
        self.data.write(data_file_path, separator = separator)
        with open(implication_file_path, 'w') as the_file:
            for i,itemset in enumerate(self.parents):
                if len(itemset)==0 : continue
                for parent in itemset:
                    the_file.write(self.data.alphabet[i]+separator+self.data.alphabet[parent]+'\n')

    @staticmethod
    def reverse(pointers):
        return [frozenset([j for j,pointer in enumerate(pointers) if i in pointer]) for i in range(len(pointers))]

    def __str__(self):
        result = "Dataset:\n"+str(self.data)+"\n\nImplications:\n"
        for i,implied in enumerate(self.parents):
            if len(implied) == 0: continue
            for parent in implied:
                result+=self.data.alphabet[i]+" "+self.data.alphabet[parent]+'\n'
        return result

    def get_filter(self, item):
        return DataWithImplication._get_filter(self.parents, item)

    @staticmethod
    def _get_filter(parents, item):
        current_filter = set([item])
        current_addables = set(parents[item])
        while current_addables:
            addable = current_addables.pop()
            if addable not in current_filter:
                current_filter.add(addable)
                current_addables|=set(parents[addable])
        return current_filter

    @staticmethod
    def get_real_filter(data, item):
        current_filter = set()
        vertical_item = data.vertical[item]
        for i, vertical_i  in enumerate(data.vertical):
            if vertical_item <= vertical_i:
                current_filter.add(i) 
            
        return current_filter

    def info(self):
        result = self.data.info()
        result+="Implications Information:\n" 
        strict_implication_relation_size = self.strict_implication_relation_size()
        strict_total_implication_relation_size = self.strict_total_implication_relation_size()
        knowledge_density = float(strict_implication_relation_size)/strict_total_implication_relation_size if strict_total_implication_relation_size>0 else 1. 
        result+="  "+"Size of provided implication basis: "+str(strict_implication_relation_size)+"\n"
        result+="  "+"Size of context implication basis:  "+str(strict_total_implication_relation_size)+"\n"
        result+="  "+"Knowledge density:                  "+("%.2f"%(knowledge_density*100))+"%"+"\n"
        return result

    def plot_implications(self):
        G = nx.DiGraph()
        G.add_nodes_from(self.data.alphabet)
        for i, parent in enumerate(self.parents):
            for j in parent:
                G.add_edge(self.data.alphabet[i], self.data.alphabet[j])
        nx.draw(G, with_labels=True, font_weight='bold')
        plt.show()
  
                
        

        
        
    
