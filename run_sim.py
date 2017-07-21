# Copyright (C) 2017 Siavoosh Payandeh Azad and Tsotne Putkaradze
# License: GNU GENERAL PUBLIC LICENSE Version 3

import os
from package import *

#TODO: get the simulator return value and check if it actually finished successfully or not!

def run_simulator(number_of_properties, tb_file_name):
	initial_file_name = tb_file_name.split(".")[0]
	for i in range(0, number_of_properties-1):
		print "-------------------------------------------------------------------------------------------"
		print "\033[32mrunning testbench: ",i,"\033[39m"
		do_file_name = "results/do_files/sim_"+str(i)+".do"
		return_value = os.system("vsim -do " + do_file_name + " -batch")
		os.rename("coverage_"+str(i)+".txt", "results/cov_files/coverage_"+str(i)+".txt")
		os.rename("coverage_"+str(i)+"_det.txt", "results/cov_files/detailed/coverage_"+str(i)+"_det.txt")
		os.rename("coverage_"+str(i)+".ucdb", "results/cov_files/coverage_"+str(i)+".ucdb")
		file = open("transcript.txt", 'r')
		for line in file:
			if "Error" in line:
				error_numbers =  int(line.split()[2][:line.split()[2].index(",")])
				if error_numbers > 0:
					raise ValueError("the simmulation has error(s)!")
	return None