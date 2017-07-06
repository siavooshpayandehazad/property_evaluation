import copy
import sys
from functions import *
from package import sys_arguments


sys_arguments = copy.deepcopy(parse_arguments(sys.argv, sys_arguments))
generate_folders()
prop_dictionary = generate_prop_dictionary(sys_arguments["input_property_file"])
report_prop_dictonary(prop_dictionary)
generate_tb(sys_arguments["testbench_file"], prop_dictionary)
generate_do_file(sys_arguments["testbench_file"], prop_dictionary)
