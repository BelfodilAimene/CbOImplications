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

from utils import current_time_in_millis
import math

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
        t = current_time_in_millis()
        data = Data.read(args.data)
        load_time = current_time_in_millis()-t
        print data.info()
        print "Data Load time:",load_time,"ms"
        cbo = CbO(data)
        cbo.start(verbose = args.verbose)

    @staticmethod
    def cboi(args):
        t = current_time_in_millis()
        dataWithImplication = DataWithImplication.read(args.data, args.implications, args.compute_implications)
        info = dataWithImplication.info()
        dataWithImplication = dataWithImplication.reduct()
        load_time = current_time_in_millis()-t
        print info
        print "Data Load time:",load_time,"ms"
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

    ## TODO: Add Graph of CbO Exectution time (ms)
    @staticmethod
    def runtest_with_different_implications(args):
        Main._test_with_different_knowledge_density(args.input_data, args.nb_cuts)

    @staticmethod
    def subdataset(args):
        dataWithImplication = DataWithImplication.read_and_reduct(args.data, args.implications, args.compute_implications)
        dataWithImplication = dataWithImplication.random_subdataset_and_subimplications(args.percentage_objects,args.percentage_attributes,args.percentage_implications)
        suffix="-{0:.2f}-{1:.2f}-{2:.2f}".format(args.percentage_objects,args.percentage_attributes,args.percentage_implications)
        dataWithImplication.write(Main._compute_output_path_from_file_path(args.data, "data", suffix),Main._compute_output_path_from_file_path(args.data, "implications", suffix))
        

    @staticmethod
    def _test_with_different_knowledge_density(data_file_path, nb_cut = 10):
        stat_file_path=Main._compute_output_path_from_file_path(data_file_path,"csv",add_suffix="-stats")
        #"""
        data_with_implications = DataWithImplication.read_and_reduct(data_file_path, None, True)
        percentages = [float(i)/nb_cut for i in range(0, nb_cut+1)]
        list_of_data = data_with_implications.random_subimplications_list(percentages)


        elapsed_time_cbo,closed_patterns_count_cbo,nb_closure_computation_cbo = CbO(data_with_implications.data).start(verbose = False, print_outputs=True)
        list_of_results = reversed(map(lambda data: CbOI(data).start(verbose = False, print_outputs=True),reversed(list_of_data)))
        
        
        x_axis = []
        y_time_axis = []
        nb_closed_axis = []
        y_generated_closed_axis = []

        execution_time_ms_cbo_axis = [elapsed_time_cbo]*len(list_of_data)

        
        
        for i,result in enumerate(list_of_results):
            x_axis.append(list_of_data[i].knowledge_density())
            y_time_axis.append(result[0])
            nb_closed_axis.append(result[1])
            y_generated_closed_axis.append(result[2])
        
        pd.DataFrame.from_dict({"density":x_axis,
                                "elapsed time ms":y_time_axis,
                                "nb closed":nb_closed_axis,
                                "nb closure":y_generated_closed_axis,
                                "elapsed time cbo":execution_time_ms_cbo_axis}).to_csv(stat_file_path,index=False, columns=["density","elapsed time ms","nb closed","nb closure", "elapsed time cbo"])
        #"""
        Main._plot_line_and_bars(stat_file_path)
           
    
    @staticmethod
    def _plot_line_and_bars(stat_file_path) :
        df = pd.read_csv(stat_file_path)
        x_axis = list(df["density"])
        y_time_axis = list(df["elapsed time ms"])
        y_generated_closed_axis = list(df["nb closure"])
        nb_closed_axis = list(df["nb closed"])
        execution_time_ms_cbo_axis = list(df["elapsed time cbo"])
        
        FONTSIZE = 18
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
        
        barWidth = [(x_axis[1]-x_axis[0])*0.75]
        for i in range(1,len(x_axis)-1):
            barWidth.append(min((x_axis[i]-x_axis[i-1])*0.75, (x_axis[i+1]-x_axis[i])*0.75))
        barWidth.append((x_axis[-1]-x_axis[-2])*0.75)
            
        barsAx.set_yscale("log")
        barsAx.bar(x_axis, y_generated_closed_axis, width = barWidth, align='center', color= "gray", alpha = 0.8)
        barsAx.bar(x_axis, nb_closed_axis, width = barWidth, align='center', color= "gray", alpha = 0.8, hatch = "//")
        timeAx.errorbar(x_axis, y_time_axis, fmt = "o-", linewidth=LINEWIDTH,markersize=MARKERSIZE,color= "black", label="CbOI")
        timeAx.errorbar(x_axis, execution_time_ms_cbo_axis, fmt = "D--", linewidth=LINEWIDTH-3,markersize=MARKERSIZE-5,color= "gray", label="CbO")
        timeAx.set_yscale("log")
        labels = [item.get_text() for item in barsAx.get_xticklabels()]

        frequency = 5
        x_axis_ticks = [(float(i)/frequency) for i in range(frequency+1)]
        plt.xticks(x_axis_ticks, map(lambda v : "{0:.0f}".format(v*100)+"%",x_axis_ticks))
        legend = timeAx.legend(loc='lower right', shadow=True, fontsize=FONTSIZE+5)
        
        
        fig.tight_layout()
        plt.savefig(Main._compute_output_path_from_file_path(stat_file_path,"pdf"))
        #plt.show()
    
    @staticmethod
    def _test(test_file_path):
        KEY_WORD = "__COMPUTE__"
        data = pd.read_csv(test_file_path)
        column_list = ["dataset_file_path","implication_file_path","nb_objects","nb_attributes",
                       "given_implication_size","context_implication_size","implications_density",
                       "data_load_time_ms","cbo_time_ms","cbo_closed_items","cbo_nb_closure_computations",
                       "data_and_implications_load_time_ms","cboi_time_ms","cboi_closed_items","cboi_nb_closure_computations"]
        result = {k:[] for k in column_list}
        output_file_name = Main._compute_output_path_from_file_path(test_file_path,"output")
        #"""
        with open(output_file_name, 'w') as f:
            pd.DataFrame.from_dict(result).to_csv(f, index=False, columns=column_list, header=True)
            for i,line in data.iterrows():
                print "Test",i,"..."
                data_file_path, implication_file_path, call_cbo = line["data_file_path"], line["implication_file_path"], line["call_cbo"]
                result["dataset_file_path"].append(data_file_path)
                result["implication_file_path"].append(implication_file_path)

                implication_file_path = str(implication_file_path)
                if implication_file_path == "nan" : implication_file_path = ""

                print "  Data file:           ",data_file_path
                print "  Implication file:    ",implication_file_path

                compute = False
                if not implication_file_path :
                    implication_file_path = None
                elif implication_file_path == KEY_WORD :
                    implication_file_path = None
                    compute = True

                instant =  current_time_in_millis()
                data = Data.read(data_file_path)
                nb_objects = data.n
                nb_attributes = data.m
                result["nb_objects"].append(nb_objects)
                result["nb_attributes"].append(nb_attributes)
                data_load_time_ms =  current_time_in_millis()-instant
                result["data_load_time_ms"].append(data_load_time_ms)
                print "  Data Load Time:                  ",data_load_time_ms,"ms"
                print "  Number of objects:               ",nb_objects
                print "  Number of attributes:            ",nb_attributes
                
                
                

                instant =  current_time_in_millis()
                dataWithImplication = DataWithImplication.read(data_file_path, implication_file_path, compute)
                
                instant2 =  current_time_in_millis()
                given_implication_size = dataWithImplication.strict_implication_relation_size()
                context_implication_size = dataWithImplication.strict_total_implication_relation_size()
                implications_density = float(given_implication_size)/context_implication_size
                instant3 = current_time_in_millis()
                dataWithImplication = dataWithImplication.reduct()
                data_and_implications_load_time_ms =  (current_time_in_millis()-instant3)+(instant2 - instant)
                result["data_and_implications_load_time_ms"].append(data_and_implications_load_time_ms)
                print "  Data and Implications Load Time: ",data_and_implications_load_time_ms,"ms"
                

                result["given_implication_size"].append(given_implication_size)
                result["context_implication_size"].append(context_implication_size)
                result["implications_density"].append(implications_density)
                print "  Given Implication Size:          ",given_implication_size
                print "  Context Implication Size:        ",context_implication_size
                print "  Implications density:            ",implications_density
                

                print "  Running CbOI (use Implications) ..."
                cboi = CbOI(dataWithImplication)
                elapsed_time, nb_closed, nb_closure = cboi.start(verbose = False, print_outputs=False)
                result["cboi_time_ms"].append(elapsed_time)
                result["cboi_closed_items"].append(nb_closed)
                result["cboi_nb_closure_computations"].append(nb_closure)
                print "    Elapsed time:                  ",elapsed_time,"ms"
                print "    Number of closed patterns:     ",nb_closed
                print "    Number of closure computations:",nb_closure
     
                
                if str(call_cbo).strip() != "no" :
                    print "  Running CbO (do not use Implications) ..."
                    cbo = CbO(data)
                    elapsed_time, nb_closed, nb_closure = cbo.start(verbose = False, print_outputs=False)
                    result["cbo_time_ms"].append(elapsed_time)
                    result["cbo_closed_items"].append(nb_closed)
                    result["cbo_nb_closure_computations"].append(nb_closure)
                    print "    Elapsed time:                  ",elapsed_time,"ms"
                    print "    Number of closed patterns:     ",nb_closed
                    print "    Number of closure computations:",nb_closure
                else:
                    result["cbo_time_ms"].append(float("nan"))
                    result["cbo_closed_items"].append(float("nan"))
                    result["cbo_nb_closure_computations"].append(float("nan"))
                print "\n\n"+"-"*40+"\n"+"-"*40+"\n\n"
                pd.DataFrame.from_dict(result)[-1:].to_csv(f, index=False, columns=column_list, header = False)
        #"""
        Latex.output_tex(output_file_name) 

    @staticmethod
    def _compute_output_path_from_file_path(file_path, extension, add_suffix = ""):
        head, tail = ntpath.split(file_path)
        tail = splitext(tail or ntpath.basename(head))[0]
        result_path = head + "/" if head else ""
        result_path+=tail+add_suffix+"."+extension
        return result_path


class Latex:
    @staticmethod
    def get_parent_dir_name(file_path):
        head, tail = ntpath.split(file_path)
        tail = splitext(tail or ntpath.basename(head))[0]
        head, tail = ntpath.split(head)
        return tail

    @staticmethod
    def textbf(string):
        return "\\textbf{"+string+"}"

    @staticmethod
    def format_int(number):
        if math.isnan(number):
            return ""
        number = int(number)
        if number == 0:
            return "0"
        result = ""
        i = 0
        while number != 0:
            if i!=0 and i%3 == 0 :
                result=" "+result
            result=str(number%10)+result
            number/=10
            i+=1
        return result
    
    @staticmethod
    def output_tex(input_file):
        data = pd.read_csv(input_file)
        output_file = Main._compute_output_path_from_file_path(input_file,"tex", add_suffix = "-xp1")
        last_cbo_time_ms = float("nan")
        last_cbo_nb_closure_computations = float("nan")
        with open(output_file, 'w') as the_file:
            for i,row in data.iterrows():
                filename = Latex.textbf(Latex.get_parent_dir_name(row["dataset_file_path"]))
                nb_objects = Latex.format_int(row["nb_objects"])
                nb_attributes = Latex.format_int(row["nb_attributes"])
                given_implication_size = Latex.format_int(row["given_implication_size"])
                context_implication_size = Latex.format_int(row["context_implication_size"])
                implications_density = "%.2f"%(row["implications_density"]*100)+"\\%"
                nb_closed = Latex.format_int(row["cboi_closed_items"])
                if not math.isnan(row["cbo_time_ms"]):    
                    cbo_time_ms = row["cbo_time_ms"]+row["data_load_time_ms"]
                    last_cbo_time_ms = cbo_time_ms
                else:
                    cbo_time_ms = last_cbo_time_ms
                cboi_time_ms = row["cboi_time_ms"]+row["data_and_implications_load_time_ms"]
                if cbo_time_ms < cboi_time_ms :
                    cbo_time_ms = Latex.textbf(Latex.format_int(cbo_time_ms))
                    cboi_time_ms = Latex.format_int(cboi_time_ms)
                elif cboi_time_ms < cbo_time_ms:
                    cboi_time_ms = Latex.textbf(Latex.format_int(cboi_time_ms))
                    cbo_time_ms = Latex.format_int(cbo_time_ms)
                
                if not math.isnan(row["cbo_nb_closure_computations"]):
                    cbo_nb_closure_computations = row["cbo_nb_closure_computations"]
                    last_cbo_nb_closure_computations = cbo_nb_closure_computations
                else:
                    cbo_nb_closure_computations = last_cbo_nb_closure_computations
                cboi_nb_closure_computations = row["cboi_nb_closure_computations"]
                if cbo_nb_closure_computations< cboi_nb_closure_computations :
                    cbo_nb_closure_computations = Latex.textbf(Latex.format_int(cbo_nb_closure_computations))
                    cboi_nb_closure_computations = Latex.format_int(cboi_nb_closure_computations)
                elif cboi_nb_closure_computations < cbo_nb_closure_computations:
                    cboi_nb_closure_computations = Latex.textbf(Latex.format_int(cboi_nb_closure_computations))
                    cbo_nb_closure_computations = Latex.format_int(cbo_nb_closure_computations)
                

                line = "&".join([str(i+1),filename,nb_objects, nb_attributes, nb_closed, given_implication_size, context_implication_size , cbo_time_ms, cbo_nb_closure_computations, cboi_time_ms, cboi_nb_closure_computations])+"\\\\"+"\n"
                the_file.write(line)
        
    
        
        
#data = Data.read("data/hmt/deputies/input.data")
#Main._test_with_different_knowledge_density(data)



if __name__=="__main__" :
    Main.main()
    #Main._test("test/test1.input")
