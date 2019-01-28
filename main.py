from numericalData import NumericalData
from hmtData import HMTData

from data import Data
from dataWithImplication import DataWithImplication

from cboi import CbOI
from cbo import CbO

from os.path import basename, splitext, dirname
import ntpath


import pandas as pd

import argparse
import subprocess

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import colors,markers

"""
NumericalData.read("data/numerical/iris.csv").interoridnal_scaling().write("data/numerical/iris-itemsets.data","data/numerical/iris-itemsets.implications")
dataWithImplication = DataWithImplication.read("data/numerical/iris-itemsets.data","data/numerical/iris-itemsets.implications")
cboi = CbOI(dataWithImplication)
cboi.start(verbose=False)
"""


"""
HMTData.read("data/hmt/input.hmt.data").ordinal_scaling().write("data/hmt/input.data","data/hmt/input.implications")
dataWithImplication = DataWithImplication.read("data/hmt/input.data","data/hmt/input.implications")
cboi = CbOI(dataWithImplication)
cboi.start(verbose=False)
"""

"""
data_file = "data/hmt/deputies/input.data"
implications_file = "data/hmt/deputies/input.implications"
dataWithImplication = DataWithImplication.read(data_file,implications_file)
cboi = CbOI(dataWithImplication)
cboi.start(verbose=False)
"""

#cbo = CbO(dataWithImplication.data)
#cbo.start(verbose=False)
    

#class Test:
#    @staticmethod


#data = DataWithImplication.read("data/numerical/BL/input.data","data/numerical/BL/input.implications")
#data = DataWithImplication.read("data/itemsets/test/test2/input.data","data/itemsets/test/test2/input.implications")
#data = DataWithImplication.read("data/numerical/test/input.data","data/numerical/test/input.implications")
#print data.knowledge_density()
#data_computed = DataWithImplication.read("data/hmt/deputies/input.data","data/hmt/deputies/input.implications", False)
#data_computed = DataWithImplication.read("data/hmt/deputies/input.data",None, True)
#print data_computed.knowledge_density()

#cboi = CbOI(data_computed)
#cboi.start(verbose=False) 
#print data_computed.knowledge_density()

class Main:
    @staticmethod
    def main():
        parser = argparse.ArgumentParser(description='ICFCA 2019 algorithms.')
        subparsers = parser.add_subparsers(title='Enumerate, Transform or Generate',
                                           description='Enumerate, Transform or Generate')

        
        
        parser_cbo=subparsers.add_parser("cbo",help="Enumerate using CbO all formal concepts")
        parser_cbo.add_argument("-d", "--data", type=str,help="filepath of dataset", required=True)
        parser_cbo.add_argument('-v','--verbose', action='store_true',help="verbose")
        parser_cbo.set_defaults(func = Main.cbo)

        parser_cboi=subparsers.add_parser("cboi",help="Enumerate using CbOI (CbO using Implications) all formal concepts")
        parser_cboi.add_argument("-d", "--data", type=str,help="filepath of dataset", required=True)
        parser_cboi.add_argument("-i", "--implications", type=str,help="filepath of implications")
        parser_cboi.add_argument('-c','--compute_implications', action='store_true',help="compute implication if implication file is not provided is not provided")
        parser_cboi.add_argument('-v','--verbose', action='store_true',help="verbose")
        parser_cboi.set_defaults(func = Main.cboi)

        parser_interordinal=subparsers.add_parser("interordinal",help="Transform a csv numerical dataset to an inter-ordinal scaled dataset with its implications")
        parser_interordinal.add_argument("input_data", type=str,help="filepath of numerical dataset")
        parser_interordinal.add_argument("-od", "--output_data", type=str,help="filepath of numerical dataset", required=False)
        parser_interordinal.add_argument("-oi", "--output_implications", type=str,help="filepath of numerical dataset", required=False)
        parser_interordinal.set_defaults(func = Main.interordinal)

        parser_ordinal=subparsers.add_parser("ordinal",help="Transform a csv dataset with a taxonomy to an ordinal scaled dataset with its implications")
        parser_ordinal.add_argument("input_data", type=str,help="filepath of dataset with a taxonomy")
        parser_ordinal.add_argument("-od", "--output_data", type=str,help="filepath of numerical dataset", required=False)
        parser_ordinal.add_argument("-oi", "--output_implications", type=str,help="filepath of numerical dataset", required=False)
        parser_ordinal.set_defaults(func = Main.ordinal)

        parser_subdataset=subparsers.add_parser("subdataset",help="compute a random sub dataset")
        parser_subdataset.add_argument("-d", "--data", type=str,help="filepath of dataset", required=True)
        parser_subdataset.add_argument("-i", "--implications", type=str,help="filepath of implications")
        parser_subdataset.add_argument('-c','--compute_implications', action='store_true',help="compute implication if implication file is not provided is not provided")
        parser_subdataset.add_argument("-po","--percentage_objects", type=float, default=1,help="the proporition of objects to keep")
        parser_subdataset.add_argument("-pa","--percentage_attributes", type=float, default=1,help="the proporition of attributes to keep")
        parser_subdataset.add_argument("-pi","--percentage_implications", type=float, default=1,help="the proporition of implications to keep after reducing the dataset")
        parser_subdataset.set_defaults(func = Main.subdataset)

        parser_test=subparsers.add_parser("test",help="Run test on a test file (two columns of file path and implication basis)")
        parser_test.add_argument("input_data", type=str,help="test file path")
        parser_test.set_defaults(func = Main.runtest)

        parser_test_with_different_implications=subparsers.add_parser("test_with_different_implications",help="Run test on a data file using different item-implication basis densities")
        parser_test_with_different_implications.add_argument("input_data", type=str,help="test file path")
        parser_test_with_different_implications.add_argument("-n", "--nb_cuts", type=int, default=10,help="number of ticks in density axis")
        parser_test_with_different_implications.set_defaults(func = Main.runtest_with_different_implications)

        args = parser.parse_args()
        args.func(args)

    @staticmethod
    def cbo(args):
        data = Data.read(args.data)
        cbo = CbO(data)
        cbo.start(verbose = args.verbose)

    @staticmethod
    def cboi(args):
        dataWithImplication = DataWithImplication.read(args.data, args.implications, args.compute_implications)
        cboi = CbOI(dataWithImplication)
        cboi.start(verbose = args.verbose)

    @staticmethod
    def interordinal(args):
        numerical_dataset = NumericalData.read(args.input_data).interoridnal_scaling()
        output_data_file = args.output_data if args.output_data else Main._compute_output_path_from_file_path(args.input_data, "data")
        output_implications_file = args.output_implications if args.output_implications else Main._compute_output_path_from_file_path(args.input_data, "implications")
        numerical_dataset.write(output_data_file,output_implications_file)

    @staticmethod
    def ordinal(args):
        hmt_dataset = HMTData.read(args.input_data).ordinal_scaling()
        output_data_file = args.output_data if args.output_data else Main._compute_output_path_from_file_path(args.input_data, "data")
        output_implications_file = args.output_implications if args.output_implications else Main._compute_output_path_from_file_path(args.input_data, "implications")
        hmt_dataset.write(output_data_file,output_implications_file)

    @staticmethod
    def runtest(args):
        Main._test(args.input_data)

    @staticmethod
    def runtest_with_different_implications(args):
        Main._test_with_different_knowledge_density(args.input_data, args.nb_cuts)

    @staticmethod
    def subdataset(args):
        dataWithImplication = DataWithImplication.read(args.data, args.implications, args.compute_implications)
        dataWithImplication = dataWithImplication.random_subdataset_and_subimplications(args.percentage_objects,args.percentage_attributes,args.percentage_implications)
        suffix="-{0:.2f}-{1:.2f}-{2:.2f}".format(args.percentage_objects,args.percentage_attributes,args.percentage_implications)
        dataWithImplication.write(Main._compute_output_path_from_file_path(args.data, "data", suffix),Main._compute_output_path_from_file_path(args.data, "implications", suffix))
        

    @staticmethod
    def _test_with_different_knowledge_density(data_file_path, nb_cut = 10):
        data_with_implications = DataWithImplication.from_data(Data.read(data_file_path), None, True)
        percentages = [float(i)/nb_cut for i in range(0, nb_cut+1)]
        list_of_data = map(data_with_implications.random_subimplications, percentages)
        
        list_of_results = reversed(map(lambda data: CbOI(data).start(verbose = False, print_outputs=True),reversed(list_of_data)))

        x_axis = []
        y_time_axis = []
        nb_closed_axis = []
        y_generated_closed_axis = []
        
        for i,result in enumerate(list_of_results):
            x_axis.append(percentages[i])
            y_time_axis.append(result[0])
            nb_closed_axis.append(result[1])
            y_generated_closed_axis.append(result[2])
        pd.DataFrame.from_dict({"density":x_axis,
                                "elapsed time ms":y_time_axis,
                                "nb closed":nb_closed_axis,
                                "nb closure":y_generated_closed_axis}).to_csv(
            Main._compute_output_path_from_file_path(data_file_path,"csv",add_suffix="-"+str(len(x_axis))+"-stats"),
            index=False, columns=["density","elapsed time ms","nb closed","nb closure"])
        Main._plot_line_and_bars(x_axis,y_time_axis,y_generated_closed_axis,nb_closed_axis, data_file_path)
           
    
    @staticmethod
    def _plot_line_and_bars(x_axis,y_time_axis,y_generated_closed_axis, nb_closed_axis, data_file_path) :
        FONTSIZE = 12
        MARKERSIZE = 20
        LINEWIDTH = 10
        
        fig, barsAx = plt.subplots()
        barsAx.set_ylabel("Closure Computation Count",fontsize=FONTSIZE)
        barsAx.set_xlabel("Density",fontsize=FONTSIZE)
        barsAx.tick_params(axis='x', labelsize=FONTSIZE)
        barsAx.tick_params(axis='y', labelsize=FONTSIZE)
        
        timeAx = barsAx.twinx()
        timeAx.set_ylabel("Execution time (ms)",fontsize=FONTSIZE)
        timeAx.tick_params(axis='y', labelsize=FONTSIZE)

        barWidth = (x_axis[1]-x_axis[0])*0.75
        barsAx.set_yscale("log")
        barsAx.bar(x_axis, y_generated_closed_axis, width = barWidth, align='center', color= "gray", alpha = 0.8)
        barsAx.bar(x_axis, nb_closed_axis, width = barWidth, align='center', color= "gray", alpha = 0.8, hatch = "//")
        timeAx.errorbar(x_axis, y_time_axis, fmt = "o-", linewidth=LINEWIDTH,markersize=MARKERSIZE,color= "black")
        timeAx.set_yscale("log")
        labels = [item.get_text() for item in barsAx.get_xticklabels()]
        
        plt.xticks(x_axis[::2], map(lambda v : "{0:.2f}".format(v*100)+"%",x_axis[::2]))
        
        
        
        fig.tight_layout()
        plt.savefig(Main._compute_output_path_from_file_path(data_file_path,"pdf",add_suffix="-"+str(len(x_axis))))
        #plt.show()
    
    @staticmethod
    def _test(test_file_path):
        data = pd.read_csv(test_file_path)
        column_list = ["dataset_file_path","implication_file_path","nb_objects","nb_attributes","implications_density",
                       "cbo_time_ms","cbo_closed_items","cbo_nb_closure_computations",
                       "cboi_time_ms","cboi_closed_items","cboi_nb_closure_computations"]
        result = {k:[] for k in column_list}
        
        for i,line in data.iterrows():
            print "Test",i,"..."
            data_file_path, implication_file_path = line[0], line[1]
            result["dataset_file_path"].append(data_file_path)
            result["implication_file_path"].append(implication_file_path)
            print "  Data file:           ",data_file_path
            print "  Implication file:    ",implication_file_path

            dataWithImplication = DataWithImplication.read(data_file_path, implication_file_path)
            nb_objects = dataWithImplication.data.n
            nb_attributes = dataWithImplication.data.m
            knowledge_density = dataWithImplication.knowledge_density()
            result["nb_objects"].append(nb_objects)
            result["nb_attributes"].append(nb_attributes)
            result["implications_density"].append(knowledge_density)
            print "  Number of objects:   ",nb_objects
            print "  Number of attributes:",nb_attributes
            print "  implications density:",knowledge_density  

            print "  Running CbOI (use Implications) ..."
            cboi = CbOI(dataWithImplication)
            elapsed_time, nb_closed, nb_closure = cboi.start(verbose = False, print_outputs=False)
            result["cboi_time_ms"].append(elapsed_time)
            result["cboi_closed_items"].append(nb_closed)
            result["cboi_nb_closure_computations"].append(nb_closure)
            print "    Elapsed time:                  ",elapsed_time,"ms"
            print "    Number of closed patterns:     ",nb_closed
            print "    Number of closure computations:",nb_closure
            
            
            cbo = CbO(dataWithImplication.data)
            elapsed_time, nb_closed, nb_closure = cbo.start(verbose = False, print_outputs=False)
            result["cbo_time_ms"].append(elapsed_time)
            result["cbo_closed_items"].append(nb_closed)
            result["cbo_nb_closure_computations"].append(nb_closure)
            print "  Running CbO (do not use Implications) ..."
            print "    Elapsed time:                  ",elapsed_time,"ms"
            print "    Number of closed patterns:     ",nb_closed
            print "    Number of closure computations:",nb_closure
        pd.DataFrame.from_dict(result).to_csv(Main._compute_output_path_from_file_path(test_file_path,"output"), index=False, columns=column_list)

    @staticmethod
    def _compute_output_path_from_file_path(file_path, extension, add_suffix = ""):
        head, tail = ntpath.split(file_path)
        tail = splitext(tail or ntpath.basename(head))[0]
        result_path = head + "/" if head else ""
        result_path+=tail+add_suffix+"."+extension
        return result_path

    
    
        
        
#data = Data.read("data/hmt/deputies/input.data")
#Main._test_with_different_knowledge_density(data)



if __name__=="__main__" :
    Main.main()
    #Main._test("test/test1.input")
