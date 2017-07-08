# Copyright (C) 2017 Siavoosh Payandeh Azad
# License: GNU GENERAL PUBLIC LICENSE Version 3

import sys
import copy
import os
import numpy as np
import string
from math import log10

def report_prop_dictonary(prop_dict):
	"""
	prints the property dictionary to the console
	returns None
	"""
	print "-----------------------------------------------------"
	print "parsed properties:"
	for item in prop_dict.keys():
		print item, "\t",
		for p in prop_dict[item]:
			print p, "\t",
		print 
	return None


def print_help():
	"""
	prints tools man to the console!
	returns None
	"""
	print "This program parses the properties fed in rtf format and generates a testbench for each property"
	print "program arguments:"
	print "\t-i [filename]:	recieves property file in rtf format. Important note, the properties should not use any internal signals!" 
	print "\t-o [filename]:	generated vhdl testbench" 
	return None


def generate_prop_dictionary(prop_file_name):
	"""
	Parses the property file fed by the user and returns a dictionary with 
	property number as the key and a list of conditions as value.
	"""
	print "-----------------------------------------------------"
	print "starting parsing the property file!"
	prop_file = open(prop_file_name, 'r')
	counter = 0
	prop_cond_dict = {}
	prop_symp_dict = {}
	for line in prop_file:
		if "G" in line:
			condition = []
			condition_section = line.split("->")[0][2:]
			if "X" not in condition_section:
				# if there is no X in the line, the we dont care about the paranthesis, we just 
				# remove them... and then split by "&"
				properties = ""
				for char in condition_section:
					if char != "(" and char != ")":
						properties += char
				condition += properties.split("&")
			elif "(" not in condition_section and ")" not in condition_section:
				# there is X in the line but there is no paranthesis
				# so we dont care!
				condition += condition_section.split("&")
			else:
				# there is X and also paranthesis in the line!
				# TODO: the problem is we only pars the first X... so there... 
				#--------------
				# happens in the first clock cycle!
				now_properties = ""
				for char in condition_section.split("X")[0][:-2]:
					if char != "(" and char != ")":
						now_properties += char
				for item in now_properties.split("&"):
					if item[0] == " ":
						item = item[1:]
					condition.append(item)
				# happens in the second clock cycle!
				later_properties = ""
				for char in condition_section.split("X")[1]:
					if char != "(" and char != ")":
						later_properties += char
				for item in later_properties.split("&"):
					if item[0] == " ":
						item = item[1:]
					condition.append("X"+item)
			prop_cond_dict[counter] = copy.deepcopy(condition)

			#TODO: parse the symptom!
			symptom = []
			symptom_section = line.split("->")[1]
			later_symptom = ""
			for char in symptom_section[symptom_section.index("("):]:
				if char != "(" and char != ")" and char != "\n" and char != "\r":
					later_symptom += char
			for item in later_symptom.split("&"):
				if item[0] == " ":
					item = item[1:]
				if "XX" in symptom_section:
					symptom.append("XX"+item)
				elif "X" in symptom_section: 
					symptom.append("X"+item)
				else:
					symptom.append(item)
			prop_symp_dict[counter] = copy.deepcopy(symptom)

			counter += 1
	print "finished parsing property file... closing file!"
	prop_file.close()
	return prop_cond_dict, prop_symp_dict


def generate_do_file(tb_file_name, prop_dictionary):
	"""
	generates a do file for modelsim for each property and stores it in results/do_files/
	returns None
	"""
	initial_file_name = tb_file_name.split(".")[0]
	for prop in prop_dictionary:
		#sim_length = len(prop_dictionary[prop])+10
		sim_length = 1000
		tb_name = "results/TB/"+initial_file_name+"_"+str(prop)+".vhd"
		do_file = open("results/do_files/sim_"+str(prop)+".do", "w")

		do_file.write("#---------------------------------------------\n")
		do_file.write("#-- THIS FILE IS GENERATED AUTOMATICALLY    --\n")
		do_file.write("#--           DO NOT EDIT                   --\n")
		do_file.write("#---------------------------------------------\n")
		do_file.write("\n")
		do_file.write("vlib work\n")
		do_file.write("\n")
		do_file.write("# Include files and compile them\n")
		do_file.write("vlog -work work  \"DUTs/state_defines.v\"\n")
		do_file.write("vlog -work work -cover bcesfx -vopt +incdir+ -cover bcesfx  \"DUTs/arbiter.v\"\n")
		do_file.write("vcom \""+tb_name+"\"\n")
		do_file.write("\n")
		do_file.write("# Start the simulation\n")
		do_file.write("vsim -coverage -voptargs=\"+cover=bcestfx\" work.property_tb\n")
		do_file.write("\n")
		do_file.write("# Run the simulation\n")
		do_file.write("run "+str(sim_length)+" ns\n")
		do_file.write("\n")
		do_file.write("# save the coverage reports\n")
		do_file.write("coverage save coverage_"+str(prop)+".ucdb\n")
		do_file.write("vcover report -output coverage_"+str(prop)+".txt coverage_"+str(prop)+".ucdb\n\n")
		do_file.write("vcover report -detail -output coverage_"+str(prop)+"_det.txt coverage_"+str(prop)+".ucdb\n\n")
		do_file.write("# Exit Modelsim after simulation\n")
		do_file.write("exit\n")

	return None


def generate_tb(tb_file_name, prop_cond_dict, prop_symp_dict):
	"""
	generates a test bench for each property and stores it in results/TB/
	returns None
	"""
	# TODO: we have to decide if it is fair that we have a wait statement for 1 clk cycle at the beginning of each testbench
	initial_file_name = tb_file_name.split(".")[0]

	for prop in prop_cond_dict:
		tb_name = "results/TB/"+initial_file_name+"_"+str(prop)+".vhd"
		print "-----------------------------------------------------"
		print "starting generation of Testbench file:", tb_name
		tb_file = open(tb_name, "w")
		tb_file.write("---------------------------------------------\n")
		tb_file.write("-- THIS FILE IS GENERATED AUTOMATICALLY    --\n")
		tb_file.write("--           DO NOT EDIT                   --\n")
		tb_file.write("---------------------------------------------\n")
		tb_file.write("--Copyright (C) 2017  Siavoosh Payandeh Azad \n\n")

		tb_file.write("library ieee;\n")
		tb_file.write("use ieee.std_logic_1164.all;\n")
		tb_file.write("use IEEE.STD_LOGIC_UNSIGNED.ALL;\n")
		tb_file.write("use IEEE.NUMERIC_STD.all;\n\n")

		tb_file.write("entity property_tb is\n")
		tb_file.write("end property_tb;\n\n")

		tb_file.write("architecture behavior of property_tb is\n\n")

		tb_file.write("-- component decleration\n")
		tb_file.write("component arbiter is\n")
		tb_file.write("port (\n")
		tb_file.write("    clk, rst: in std_logic;\n")
		tb_file.write("    Lflit_id, Nflit_id, Eflit_id, Wflit_id, Sflit_id: in std_logic_vector(2 downto 0);\n")
		tb_file.write("    Llength, Nlength, Elength, Wlength, Slength: in std_logic_vector(11 downto 0);\n")
		tb_file.write("    Lreq, Nreq, Ereq, Wreq, Sreq: in std_logic;\n")
		tb_file.write("    nextstate: out std_logic_vector(5 downto 0)\n")
		tb_file.write(");\n")
		tb_file.write("end component;\n\n")

		tb_file.write("signal nextstate: std_logic_vector(5 downto 0) := (others => '0');\n")
		tb_file.write("signal Lflit_id, Nflit_id, Eflit_id, Wflit_id, Sflit_id: std_logic_vector(2 downto 0):= (others => '0');\n")
		tb_file.write("signal Llength, Nlength, Elength, Wlength, Slength: std_logic_vector(11 downto 0):= (others => '0');\n")
		tb_file.write("signal Lreq, Nreq, Ereq, Wreq, Sreq: std_logic := '0';\n")
		tb_file.write("signal clk, rst : std_logic := '1';\n")
		tb_file.write("constant clk_period : time := 1 ns;\n")
		tb_file.write("\nbegin\n\n")

		tb_file.write("-- clock generation!\n")
		tb_file.write("    clk_process :process\n")
		tb_file.write("    begin\n")
		tb_file.write("        clk <= '0';\n")
		tb_file.write("        wait for clk_period/2;\n")
		tb_file.write("        clk <= '1';\n")
		tb_file.write("        wait for clk_period/2;\n")
		tb_file.write("    end process;\n\n")

		tb_file.write("\n\n-- instantiate the compoent\n")
		tb_file.write("DUT: arbiter\n")
		tb_file.write("     port map(clk, rst, Lflit_id, Nflit_id, Eflit_id, Wflit_id, Sflit_id, Llength, Nlength, Elength, Wlength, Slength, Lreq, Nreq, Ereq, Wreq, Sreq, nextstate);")

		tb_file.write("\n\n-- applying the stimuli\n")
		tb_file.write("    process begin\n")
		tb_file.write("        wait for 1 ns;\n")
		next_clk = False
		for item in prop_cond_dict[prop]:
			if 'X' in item:
				item = item [item.index("X")+1:]
				if next_clk == False :
					tb_file.write("        wait for 1 ns;\n")
					next_clk = True
			if "!" in item:
				index = item.split()[0].index("!")
				signal_name = item.split()[0][index+1:]
				digit =  [int(s) for s in signal_name if s.isdigit()]
				if len(digit)>0:
					signal_name = signal_name[:signal_name.index(str(digit[0]))-1]+"("+str(digit[0])+")"
				tb_file.write("        "+signal_name+" <= '0';\n")
			else:
				if item != "1 ":
					signal_name = item.split()[0]
					digit =  [int(s) for s in signal_name if s.isdigit()]
					if len(digit)>0:
						signal_name = signal_name[:signal_name.index(str(digit[0]))-1]+"("+str(digit[0])+")"
					tb_file.write("        "+signal_name+" <= '1';\n")
		tb_file.write("        wait;\n")
		tb_file.write("    end process;\n\n")

		tb_file.write("\n\n-- checking the symptom\n")
		tb_file.write("    process begin\n")
		for symptom in prop_symp_dict[prop]: 
			wait  = 0
			value = 1
			symptom = symptom.replace("[", "(")
			symptom = symptom.replace("]", ")")
			if "XX" in symptom and wait < 2:
				wait =  2
				tb_file.write("        wait for 2 ns;\n")
				symptom = symptom[symptom.index("X")+2:]
			elif "X" in symptom and wait < 1:
				wait =  1
				tb_file.write("        wait for 1 ns;\n")
				symptom = symptom[symptom.index("X")+1:]
			if "!" in symptom:
				symptom = symptom[symptom.index("!")+1:]
				value = 0
			tb_file.write("        assert "+str(symptom)+" = "+ str(value)+ " report \"ASSIRTION FAILED\" severity failure;\n")
		tb_file.write("        wait;\n")
		tb_file.write("    end process;\n\n")

		tb_file.write("\nEND;\n")

		print "finished generation of Testbench... closing the file!"
		tb_file.close()
	return None


def parse_arguments(sys_args, package_arguments):
	"""
	Parses the argumets passed to the tool and updates the package arguments accordingly
	Returns package arguement in form of a dictionary
	"""

	if "--help" in sys.argv[:]:
		print_help()
		sys.exit()

	if "-i" in sys.argv[:]:
		package_arguments["input_property_file"] = sys.argv[sys.argv.index("-i")+1]
		if ".rtf" not in package_arguments["input_property_file"] :
			raise ValueError("property file should be in rtf format")
	else:
		raise ValueError ("a valid property file is needed!")

	if "-o" in sys.argv[:]:
		package_arguments["testbench_file"] = sys.argv[sys.argv.index("-o")+1]
	else:
		package_arguments["testbench_file"] = "tb.vhd"
	return package_arguments


def generate_folders():
	"""
	Generates the folder structure as follows:
	
	|_results
		|
		|___TB 					for storing all generated testbenches
		|___do_files 			for storing all generated testbenches
		|___cov_files 			for storing all generated coverage reports
				|___detailed 	for storing all generated detailed coverage reports

	cleans the folders if some files are remaining from previous runs. however, it only
	removes the files with .vhd extention from TB folder and with .do extention from 
	do_files folder.
	returns None
	"""
	if not os.path.exists("results"):
		os.makedirs("results")

	if not os.path.exists("results/TB"):
		os.makedirs("results/TB")
	else:
		file_list = [vhd_file for vhd_file in os.listdir("results/TB") if vhd_file.endswith(".vhd")]
		for vhd_file in file_list:
			os.remove('results/TB/'+vhd_file)
	if not os.path.exists("results/do_files"):
		os.makedirs("results/do_files")
	else:
		file_list = [do_file for do_file in os.listdir("results/do_files") if do_file.endswith(".do")]
		for do_file in file_list:
			os.remove('results/do_files/'+do_file)

	if not os.path.exists("results/cov_files"):
		os.makedirs("results/cov_files")
	else:
		file_list = [cov_file for cov_file in os.listdir("results/cov_files")if cov_file.endswith(".txt") or cov_file.endswith(".ucdb")]
		for cov_file in file_list:
			os.remove('results/cov_files/'+cov_file)

	if not os.path.exists("results/cov_files/detailed"):
		os.makedirs("results/cov_files/detailed")
	else:
		file_list = [cov_file for cov_file in os.listdir("results/cov_files/detailed")if cov_file.endswith(".txt")]
		for cov_file in file_list:
			os.remove('results/cov_files/detailed/'+cov_file)
	return None


def parse_cov_reports():
	"""
	parses the short coverage reports! 
	will generate a table where each row i shows different coverage parameters for property i
	also, will provide some statistic in form of a histogram showing number of properties vs. 
	their statement coverage.
	returns None
	"""
	covg_dictionary = {}
	for filename in os.listdir("results/cov_files"):
		if filename.endswith(".txt"):
			property_number = int(filename[filename.index("_")+1:filename.index(".")])
			covg_dictionary[property_number] =[]
			file = open("results/cov_files/"+filename, 'r')
			for line in file:
				if "Stmts" in line:
					covg_dictionary[property_number].append(line.split()[-1])
				if "Branches" in line:
					covg_dictionary[property_number].append(line.split()[-1])
				if "States" in line:
					covg_dictionary[property_number].append(line.split()[-1])
				if "Transitions" in line:
					covg_dictionary[property_number].append(line.split()[-1])
				if "Toggle" in line:
					covg_dictionary[property_number].append(line.split()[-1])
				if "Total" in line:
					covg_dictionary[property_number].append(line.split()[-1])

	max_total = 0
	best_property = None
	total_coverage_list = []
	print "#\tstmt\tbranch\tstate\ttrans\ttggl\ttotal"
	print "-------------------------------------------------------"
	for item in range(0, len(covg_dictionary.keys())):
		
		print item, "\t",
		for percentage in covg_dictionary[item]:
			print percentage,"\t",
		print 
		total_coverage_list.append(float(covg_dictionary[item][-1][:-1]))
		if max_total < float(covg_dictionary[item][-1][:-1]):
			max_total = float(covg_dictionary[item][-1][:-1])
			best_property = item
	print "-------------------------------------------------------"
	print "max total coverage for single property:", max_total
	print "best property:", best_property

	print "-------------------------------------------------------"
	print "histogram of total coverage of properties"
	bins = 20
	h,b = np.histogram(sorted(total_coverage_list+[max_total+1]), bins)

	for i in range (0, bins-1):
		print string.rjust(`b[i]`, 7)[:int(log10(np.amax(b)))+5], '| ', '*'*int(70*h[i-1]/np.amax(h))
	print string.rjust(`b[bins]`, 7)[:int(log10(np.amax(b)))+5] 
	print "-------------------------------------------------------"
	return None


def parse_det_cov_report():
	"""
	parses the detailed coverage and prints the list of properties that hit each statement in the design
	returns stmt_covg_dictionary which is a dictionary with line numbers as keys and list of properties covering
	that line as value:
		stmt_covg_dictionary = { line_number_0: [list of properties covering line 0],
					  		   line_number_1: [list of properties covering line 1],
					  		   ...
		}
	"""
	stmt_covg_dictionary = {}
	for filename in os.listdir("results/cov_files/detailed"):
		if filename.endswith(".txt"):
			file = open("results/cov_files/detailed/"+filename, 'r')
			enable = False
			tb_number = int(filename[filename.index("_")+1:filename.index(".")][:-4])
			for line in file:
				if "Branch Coverage:" in line:
					enable = False
					break
				if enable:
					parameters = []
					for item in line[:50].split(" "):
						if item != '' : 
							parameters.append(item)
					if len(parameters)> 1:
						if parameters[2] != '***0***':
							if int(parameters[0]) not in stmt_covg_dictionary.keys():
								stmt_covg_dictionary[int(parameters[0])]= [tb_number]
							else:
								if tb_number not in stmt_covg_dictionary[int(parameters[0])]:
									stmt_covg_dictionary[int(parameters[0])].append(tb_number)
				if "Statement Coverage for" in line:
					enable = True
	for index in sorted(stmt_covg_dictionary.keys()):
		print index, "\t", sorted(stmt_covg_dictionary[index])
	return stmt_covg_dictionary


def remove_covered_statements(stmt_covg_dictionary, property_id):
	"""
	removes statemets from property dictionary "stmt_covg_dictionary" which are covered by property "property_id"
	returns refined stmt_covg_dictionary
	"""
	deletion_list = []
	for item in stmt_covg_dictionary.keys():
		if property_id in stmt_covg_dictionary[item]:
			deletion_list.append(item)
	for del_item in deletion_list:
		del stmt_covg_dictionary[del_item]
	return stmt_covg_dictionary


def find_most_covering_prop (stmt_covg_dictionary):
	"""
	goes thorugh the property dictionary with the following strucutre:
		stmt_covg_dictionary = { line_number_0: [list of properties covering line 0],
								 line_number_1: [list of properties covering line 1],
					  			 ...
		}
	and returns the property which covers most number of lines.

	"""
	big_list = []
	for item in stmt_covg_dictionary.keys():
		big_list += stmt_covg_dictionary[item]
	most_covering_prop =  max(set(big_list), key=big_list.count)
	return most_covering_prop
