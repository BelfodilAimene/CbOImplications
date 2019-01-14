import numpy as np
import pandas as pd
from data import Data
from dataWithImplication import DataWithImplication

class HMTData :
    def __init__(self, items):
        self.items = items
        
        

    def ordinal_scaling(self):
        """
        # HMT items dataset are separated by . 3.10.1 imply 3 items 3.10.1 -> 3.10 -> 3
        """
        alphabet = set()
        for itemset in self.items:
            for hmt_item in itemset:
                alphabet|=HMTData.get_items_from_hmt_item(hmt_item)

        alphabet = sorted(alphabet)
        symbol_to_indice = {symbol:i for i,symbol in enumerate(alphabet)}
        horizontal = []
        for itemset in self.items:
            new_itemset = set()
            for item in itemset :
                hmt_items = HMTData.get_items_from_hmt_item(item)
                for element in hmt_items:
                    new_itemset.add(symbol_to_indice[element])
            horizontal.append(frozenset(new_itemset))
        
        data = Data.from_horizontal(alphabet, horizontal)
        parents = []
        for element in alphabet:
            if "." not in element:
                parents.append(frozenset())
            else :
                parents.append(frozenset([symbol_to_indice[".".join(element.split(".")[:-1])]]))

        childs = DataWithImplication.get_parents_from_childs_or_childs_from_parents(parents)

        return DataWithImplication(data, childs, parents)

    @staticmethod
    def get_items_from_hmt_item(hmt_item):
        if len(hmt_item)==0:
            return frozenset()
        splitted = hmt_item.split(".")
        prefix = splitted[0]
        result = set([prefix])
        for element in splitted[1:]:
            prefix+="."+element
            result.add(prefix)
        return result
    @staticmethod
    def read(hmt_file_path):
        with open(hmt_file_path, 'r') as f:
            all_lines = f.readlines()
            itemsets = map(lambda e : frozenset() if e in (" \n"," ") else frozenset(map(str,e.replace("\n","").split(" "))),all_lines)
        return HMTData(itemsets)
    

    
        



