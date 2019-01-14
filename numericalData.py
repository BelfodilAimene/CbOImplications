import numpy as np
import pandas as pd
from data import Data
from dataWithImplication import DataWithImplication

class NumericalData :
    def __init__(self, dataframe):
        self.dataframe = dataframe

    def interoridnal_scaling(self):
        """
        produce a DataWithImplications
        """
        columns = list(self.dataframe.columns)
        
        values = [sorted(set(self.dataframe[column])) for column in columns]
        value_to_indice_per_column = [{value:i for i, value in enumerate(sorted_vals)} for sorted_vals in values]
        # For each attribute attr a tuple of two indice :
        #   The first indice indicates the indice of the first item of the 'attr<=value' items for decrasing values
        #   The second one indicatesthe indice of the first item of the 'attr>=value' items for increasing values
        attr_to_items_indices = []
        
        alphabet = []
        for column,list_of_values in zip(columns, values):
            first_indice = len(alphabet)
            for value in list_of_values:
                alphabet.append(column.strip()+">="+str(value))
            second_indice = len(alphabet)
            for value in reversed(list_of_values):
                alphabet.append(column.strip()+"<="+str(value))
            attr_to_items_indices.append((first_indice,second_indice))
        

        horizontal = []
        for _,row in self.dataframe.iterrows():
            row = list(row)
            itemset = []
            for column_indice,value in enumerate(row):
                next_column_first_indice = len(alphabet) if column_indice==len(columns)-1 else attr_to_items_indices[column_indice+1][0]

                value_internal_indice = value_to_indice_per_column[column_indice][value]
                itemset += range(attr_to_items_indices[column_indice][0],attr_to_items_indices[column_indice][0]+value_internal_indice+1)
                itemset += range(attr_to_items_indices[column_indice][1],next_column_first_indice-value_internal_indice)
                

            horizontal.append(set(itemset))
             
        data = Data.from_horizontal(alphabet, horizontal)

        childs = []
        
        for column, item_indices in enumerate(attr_to_items_indices):
            next_column_first_indice = len(alphabet) if column==len(columns)-1 else attr_to_items_indices[column+1][0]
            for i in range(attr_to_items_indices[column][0],attr_to_items_indices[column][1]-1):
                childs.append(frozenset([i+1]))
            childs.append(frozenset())
            for i in range(attr_to_items_indices[column][1],next_column_first_indice-1):
                childs.append(frozenset([i+1]))
            childs.append(frozenset())
        parents = DataWithImplication.get_parents_from_childs_or_childs_from_parents(childs)

        return DataWithImplication(data, childs, parents)
        

    @staticmethod
    def read(csv_path):
        data = pd.read_csv(csv_path)
        return NumericalData(data)
    

    def __str__(self):
        return str(self.dataframe)
        
