import numpy as np
import pandas as pd
from data import Data
from dataWithImplication import DataWithImplication
from utils import _compute_output_path_from_file_path


    

class ComplexData :
    attribute_type_to_scale_function = {"nominal":"nominal_scale",
                                        "ordinal":"ordinal_scale",
                                        "interordinal":"interordinal_scale"}

    
    def __init__(self, dataframe, attribute_types = []):
        self.dataframe = dataframe
        self.attribute_types = attribute_types
        self.attribute_names = list(dataframe.columns)

    def scale(self):
        result = [[] for _ in range(self.dataframe.shape[0])]
        implications = set()

        for attribute_type, attribute_name in zip(self.attribute_types, self.attribute_names):
            attribute_values = list(self.dataframe[attribute_name])
            
            attr_result, attr_implications = ComplexData.attribute_scale(attribute_type,attribute_name, attribute_values)
            implications |= attr_implications
            for i,value in enumerate(attr_result):
                result[i].extend(value)
        return BasicContextAndImplications(result, implications)

    @staticmethod
    def read_scale_and_write(input_path, output_data_path = None, output_implications_path = None):
        output_data_path = _compute_output_path_from_file_path(input_path,"data") if output_data_path == None else output_data_path
        output_implications_path = _compute_output_path_from_file_path(input_path,"implications") if output_implications_path == None else output_implications_path
        ComplexData.read(input_path).scale().write(output_data_path,output_implications_path)
        
    @staticmethod
    def read(csv_path):
        data = pd.read_csv(csv_path, header=0, skiprows = 1)
        attribute_types = pd.read_csv(csv_path, header=None, nrows=1)
        return ComplexData(data, list(attribute_types.loc[0]))

    @staticmethod
    def attribute_scale(column_type,column_name, column_values):
        
        if column_type not in ComplexData.attribute_type_to_scale_function:
            raise Exception(column_type+" scale is not supported")
        return getattr(ComplexData,ComplexData.attribute_type_to_scale_function[column_type])(column_name,column_values)

    @staticmethod
    def nominal_scale(column_name, column_values):
        return [[column_name+"="+value] for value in column_values], set()

    @staticmethod
    def ordinal_scale(column_name, column_values):
        result = []
        implications = set()
        for value in column_values:
            new_value = set()
            for item in value.split(" "):
                list_of_one_items = map(lambda x : column_name+"-is-"+x, ComplexData.get_items_from_hmt_item(item))
                if len(list_of_one_items)>0:
                    new_value.add(list_of_one_items[0])
                    for i in range(1, len(list_of_one_items)):
                        implications.add((list_of_one_items[i],list_of_one_items[i-1]))
                        new_value.add(list_of_one_items[i])
            result.append(sorted(new_value))    
        #return [sorted(set([column_name+":"+one_item for item in value.split(" ") for one_item in ComplexData.get_items_from_hmt_item(item)])) for value in column_values]
        return result, implications

    @staticmethod
    def interordinal_scale(column_name, column_values):
        sorted_values = sorted(set(column_values))
        value_to_indice_per_column = {value:i for i, value in enumerate(sorted_values)}

        result=[]
        implications = set()
        for i in range(len(sorted_values)-1):
            implications.add((column_name+"<="+str(sorted_values[i]),column_name+"<="+str(sorted_values[i+1])))
            implications.add((column_name+">="+str(sorted_values[i+1]),column_name+">="+str(sorted_values[i])))

        for value in column_values:
            new_value = set()
            indice = value_to_indice_per_column[value]
            for i in range(indice+1):
                new_value.add(column_name+">="+str(sorted_values[i]))
            for i in range(indice, len(value_to_indice_per_column)):
                new_value.add(column_name+"<="+str(sorted_values[i]))
            result.append(sorted(new_value))
            
            
        return result, implications
            
        

    @staticmethod
    def get_items_from_hmt_item(hmt_item):
        if len(hmt_item)==0:
            return []
        splitted = hmt_item.split(".")
        prefix = splitted[0]
        result = [prefix]
        for element in splitted[1:]:
            prefix+="."+element
            result.append(prefix)
        return result


class BasicContextAndImplications :

    def __init__(self, horizontal, implications):
        self.horizontal = horizontal
        self.implications = implications
        

    def write(self, data_file_path, implication_file_path):
        with open(data_file_path, "w") as data_file:
            for value in self.horizontal :
                data_file.write("\t".join(value)+"\n")
        
        with open(implication_file_path, "w") as implication_file:
            for value in self.implications :
                implication_file.write("\t".join(value)+"\n")
                
        
    def __str__(self):
        result = "Itemsets:\n"
        for value in self.horizontal :
            result+="  "+" ".join(value)+"\n"
        result += "\nImplications:\n"
        for a,b in self.implications:
            result+="  "+(a+" -> "+b)+"\n"
        return result


