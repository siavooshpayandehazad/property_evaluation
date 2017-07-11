# Copyright (C) 2017 Siavoosh Payandeh Azad
# License: GNU GENERAL PUBLIC LICENSE Version 3

import copy
import sys
from functions import *
from package import sys_arguments
from run_sim import run_simulator

# TODO: check if everything is ok with the user's system! if there is a library dependency missing etc...

sys_arguments = copy.deepcopy(parse_arguments(sys.argv, sys_arguments))					# parse the user inputs
generate_folders()		# generates folder structure
prop_cond_dict, prop_symp_dict = generate_prop_dictionary(sys_arguments["input_property_file"])		# parse the property recieved from input file 
report_prop_dictonary(prop_cond_dict)		# prints contecnt of the the property dictionary to console
generate_tb(sys_arguments["testbench_file"], prop_cond_dict, prop_symp_dict)	# generates the TB lists
generate_do_file(sys_arguments["testbench_file"], prop_cond_dict)	# generates the do files
run_simulator(len(prop_cond_dict), sys_arguments["testbench_file"])	# runs the simulator and generates the coverage reports!
parse_cov_reports()		# parse normal coverage reports and provide statistics
covg_dictionary = parse_det_cov_report() # parse detail coverage reports!
find_minimal_set_of_properties_stmt(covg_dictionary)	# finds minimal set of properties that covers every statement.