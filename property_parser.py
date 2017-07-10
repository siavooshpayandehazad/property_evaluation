# Copyright (C) 2017 Siavoosh Payandeh Azad
# License: GNU GENERAL PUBLIC LICENSE Version 3

import copy
import sys
from functions import *
from package import sys_arguments
from run_sim import run_simulator

sys_arguments = copy.deepcopy(parse_arguments(sys.argv, sys_arguments))					# parse the user inputs
generate_folders()		# generates folder structure
prop_cond_dict, prop_symp_dict = generate_prop_dictionary(sys_arguments["input_property_file"])		# parse the property recieved from input file 
report_prop_dictonary(prop_cond_dict)		# prints contecnt of the the property dictionary to console
generate_tb(sys_arguments["testbench_file"], prop_cond_dict, prop_symp_dict)	# generates the TB lists
generate_do_file(sys_arguments["testbench_file"], prop_cond_dict)	# generates the do files
run_simulator(len(prop_cond_dict), sys_arguments["testbench_file"])
parse_cov_reports()
covg_dictionary = parse_det_cov_report()

taken_properties = []
while (len(covg_dictionary.keys())>0):
	best_prop = find_most_covering_prop (covg_dictionary)
	taken_properties.append(best_prop)
	remove_covered_statements(covg_dictionary, best_prop)

print "Set of statements that cover every statement coverd by initial set:", taken_properties