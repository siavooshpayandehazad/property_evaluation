# Copyright (C) 2017 Siavoosh Payandeh Azad
# License: GNU GENERAL PUBLIC LICENSE Version 3

import sys
import copy
import os
import numpy as np
import string
from math import log10
from package import *
import os.path

def report_prop_dictonary(prop_dict):
	"""
	prints the property dictionary to the console
	returns None
	"""
	if not isinstance(prop_dict, dict):
		raise ValueError("prop_dict is not a dictionary!")
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
	#TODO:
	print "\nTODO:"
	print "     * We need to improve the property parser (for both condition and symptom)... its very primitive now!"
	print "     * The parser doesnt parse different inputs... somehow we need to fix that!"
	print "     * the coverage parser should be extended to also provide the branch and other coverage results!"
	return None


def generate_prop_dictionary(prop_file_name):
	"""
	Parses the property file fed by the user and returns a dictionary with 
	property number as the key and a list of conditions as value.
	"""
	if not isinstance(prop_file_name, str):
		raise ValueError("prop_file_name is not a string!")
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
			if not os.path.isfile(package_arguments["input_property_file"]):
				print "input propoerty file path is not valid"
				sys.exit()
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
		|		|___detailed 	for storing all generated detailed coverage reports
		|___reports 			stors tool generated reports!

	cleans the folders if some files are remaining from previous runs. however, it only
	removes the files with .vhd extention from TB folder and with .do extention from 
	do_files folder.
	returns None
	"""
	if not os.path.exists(results_path):
		os.makedirs(results_path)

	if not os.path.exists(tb_path):
		os.makedirs(tb_path)
	else:
		file_list = [vhd_file for vhd_file in os.listdir(tb_path) if vhd_file.endswith(".vhd")]
		for vhd_file in file_list:
			os.remove(tb_path+"/"+vhd_file)

	if not os.path.exists(do_path):
		os.makedirs(do_path)
	else:
		file_list = [do_file for do_file in os.listdir(do_path) if do_file.endswith(".do")]
		for do_file in file_list:
			os.remove(do_path+"/"+do_file)

	if not os.path.exists(cov_path):
		os.makedirs(cov_path)
	else:
		file_list = [cov_file for cov_file in os.listdir(cov_path)if cov_file.endswith(".txt") or cov_file.endswith(".ucdb")]
		for cov_file in file_list:
			os.remove(cov_path+'/'+cov_file)

	if not os.path.exists(cov_detailed_path):
		os.makedirs(cov_detailed_path)
	else:
		file_list = [cov_file for cov_file in os.listdir(cov_detailed_path)if cov_file.endswith(".txt")]
		for cov_file in file_list:
			os.remove(cov_detailed_path+'/'+cov_file)

	if not os.path.exists(reports_path):
		os.makedirs(reports_path)
	else:
		file_list = [report_file for report_file in os.listdir(reports_path)if report_file.endswith(".txt")]
		for report_file in file_list:
			os.remove(reports_path+"/"+report_file)

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
	file = open("results/reports/general_stmt_coverage_report.txt","w")
	file.write("#\tstmt\tbranch\tstate\ttrans\ttggl\ttotal\n")
	file.write("-------------------------------------------------------\n")
	for item in range(0, len(covg_dictionary.keys())):
		
		file.write( item, "\t",)
		for percentage in covg_dictionary[item]:
			file.write( percentage,"\t",)
		file.write("\n") 
		total_coverage_list.append(float(covg_dictionary[item][-1][:-1]))
		if max_total < float(covg_dictionary[item][-1][:-1]):
			max_total = float(covg_dictionary[item][-1][:-1])
			best_property = item
	file.write("-------------------------------------------------------\n")
	file.write("max total coverage for single property:" +str(max_total)+"\n")
	file.write("best property:" +str(best_property)+"\n")
	file.close()

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
			file.close()
	file = open("results/reports/detailed_stmt_coverage_report.txt","w")
	for index in sorted(stmt_covg_dictionary.keys()):
		print index, "\t", sorted(stmt_covg_dictionary[index])
		file.write(str(index)+"\t")
		for itme in stmt_covg_dictionary[index]:
			file.write(str(item)," ,")
		file.write("\n")
	file.close()
	return stmt_covg_dictionary


def remove_covered_statements(stmt_covg_dictionary, property_id):
	"""
	removes statemets from property dictionary "stmt_covg_dictionary" which are covered by property "property_id"
	returns refined stmt_covg_dictionary
	"""
	# TODO: check if stmt_covg_dictionary is dictionary, check property_id
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


def find_minimal_set_of_properties_stmt(stmt_covg_dictionary):
	"""
	returns a list of properties that cover all the statements in the cov_dictionary. 
	"""
	print "Starting the process of finding a sub-set of properties that cover everything covered by initial set!"
	taken_properties = []
	while (len(stmt_covg_dictionary.keys())>0):
		best_prop = find_most_covering_prop(stmt_covg_dictionary)
		taken_properties.append(best_prop)
		remove_covered_statements(stmt_covg_dictionary, best_prop)

	print "number of properties in the sub-set:", len(taken_properties) 
	print "final set:", taken_properties
	print "----------------------------------------"
	return taken_properties

