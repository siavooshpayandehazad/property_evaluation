# Copyright (C) 2017 Siavoosh Payandeh Azad
# License: GNU GENERAL PUBLIC LICENSE Version 3
import copy


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
