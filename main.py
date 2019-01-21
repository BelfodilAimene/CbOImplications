from data import Data
from dataWithImplication import DataWithImplication
from cboi import CbOI
from cbo import CbO
from numericalData import NumericalData
from hmtData import HMTData


#numericalData.interoridnal_scaling().write("data/numerical/iris-itemsets.data","data/numerical/iris-itemsets.implications")
#hmtData = HMTData.read("data/hmt/input.hmt.data").ordinal_scaling().write("data/hmt/input.data","data/hmt/input.implications")


#dataWithImplication =  NumericalData.read("data/numerical/iris.csv").interoridnal_scaling()
#dataWithImplication = DataWithImplication.read("data/input0/input0.data","data/input0/input0-full.implications")
dataWithImplication = DataWithImplication.read("data/numerical/iris-itemsets.data","data/numerical/iris-itemsets.implications")
#dataWithImplication = DataWithImplication.read("data/hmt/input.hmt.data","data/hmt/input.implications")
#dataWithImplication = DataWithImplication.read("data/hmt/input.hmt.data",None, False)

#print dataWithImplication.data.alphabet
#dataWithImplication = dataWithImplication.sorted_alphabet_dataset_with_implications()

#print dataWithImplication.data.alphabet
#print numericalData


#dataWithImplication = DataWithImplication.read("data/input0/input0.data", "data/input0/input0-empty.implications")
#dataWithImplication = DataWithImplication.read("data/numerical/iris-itemsets.data","data/numerical/iris-itemsets.implications")
cboi = CbOI(dataWithImplication)
cboi.start(verbose=False)

#data = Data.read("input0/input0.data")
#cbo = CbO(dataWithImplication.data)
#cbo.start(verbose=False)   
#print d._get_column_clarified_dataset() 
    
    
