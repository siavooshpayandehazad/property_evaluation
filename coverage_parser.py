# Copyright (C) 2017 Siavoosh Payandeh Azad
# License: GNU GENERAL PUBLIC LICENSE Version 3
from package import *
import os 
import numpy as np
import string
from math import log10


def parse_cov_reports():
	"""
	parses the short coverage reports! 
	will generate a table where each row i shows different coverage parameters for property i
	also, will provide some statistic in form of a histogram showing number of properties vs. 
	their statement coverage.
	returns None
	"""
	covg_dictionary = {}
	for filename in os.listdir(cov_path):
		if filename.endswith(".txt"):
			property_number = int(filename[filename.index("_")+1:filename.index(".")])
			covg_dictionary[property_number] =[]
			file = open(cov_path+"/"+filename, 'r')
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
	file = open(reports_path+"/general_stmt_coverage_report.txt","w")
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
	for filename in os.listdir(cov_detailed_path):
		if filename.endswith(".txt"):
			file = open(cov_detailed_path+"/"+filename, 'r')
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
	file = open(reports_path+"/detailed_stmt_coverage_report.txt","w")
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