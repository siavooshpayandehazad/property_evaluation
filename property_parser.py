import copy
import sys
from functions import *
from package import sys_arguments


sys_arguments = copy.deepcopy(parse_arguments(sys.argv, sys_arguments))					# parse the user inputs
generate_folders()		# generates folder structure
prop_dictionary = generate_prop_dictionary(sys_arguments["input_property_file"])		# parse the property recieved from input file 
report_prop_dictonary(prop_dictionary)		# prints contecnt of the the property dictionary to console
generate_tb(sys_arguments["testbench_file"], prop_dictionary)	# generates the TB lists
generate_do_file(sys_arguments["testbench_file"], prop_dictionary)	# generates the do files
