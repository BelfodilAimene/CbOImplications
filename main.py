from numericalData import NumericalData
from hmtData import HMTData

from data import Data
from dataWithImplication import DataWithImplication

from cboi import CbOI
from cbo import CbO

from os.path import basename, splitext, dirname
import ntpath

import argparse
import subprocess

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

data_file = "data/hmt/deputies/input.data"
implications_file = "data/hmt/deputies/input.implications"
dataWithImplication = DataWithImplication.read(data_file,implications_file)
cboi = CbOI(dataWithImplication)
cboi.start(verbose=False)
    

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
    def _compute_output_path_from_file_path(file_path, extension):
        head, tail = ntpath.split(file_path)
        tail = splitext(tail or ntpath.basename(head))[0]
        result_path = head + "/" if head else ""
        result_path+=tail+"."+extension
        return result_path
        
        


if __name__=="__main__" :
    Main.main()
