# Copyright (C) 2017 Siavoosh Payandeh Azad
# License: GNU GENERAL PUBLIC LICENSE Version 3

from math import log

def generate_prop_dictionary_sva(prop_file_name):

	if not isinstance(prop_file_name, str):
		raise ValueError("prop_file_name is not a string!")
	print "-----------------------------------------------------"
	print "starting parsing the property file!"
	prop_file = open(prop_file_name, 'r')

	counter = 0
	prop_cond_dict = {}
	prop_symp_dict = {}
	for line in prop_file:
		delay = None
		repeat_sequence = None
		current_cycle_prop = None
		# TODO: fix property nextstate_184;
		if "endmodule" in line:	# this is the end of usefull part!
			break
		if "(rst)" in line:
			dict_delay = 0
			prop_cond_dict[counter] = []
			delay = 0
			repeat_sequence = None
			current_cycle_prop  = "(rst)"
		if "##" in line and "|->" not in line: 
			delay = line[line.index("##")+2:line.index("(")]
			current_cycle_prop = line[line.index("("):]
		if "[*" in line:
			repeat_start = line.index("[*") 
			repeat_end  = line.index("]")
			repeat_sequence = line[repeat_start+2:repeat_end]
			current_cycle_prop = current_cycle_prop[:current_cycle_prop.index("[*")]
		if current_cycle_prop != None:
			prop = ""
			for char in current_cycle_prop:
				if char != "(" and char != ")" and char != "\n" and char != "\r" and char != " ":
					prop += char

			refined_list = []
			for item in prop.split("&&"):
				if "==" in item:
					refined_list.append(item[:item.index("=")])
				else:
					refined_list.append(item)
			if repeat_sequence != None:
				if ":" not in repeat_sequence:
					for i in range(0, int(repeat_sequence)):
						dict_delay += int(delay)
						for item in refined_list: 
							prop_cond_dict[counter].append(dict_delay*"X"+item)
				else:
					repeat = 1
					if repeat_sequence.split(":")[1] != "$":
						repeat  = repeat_sequence.split(":")[1]
					else:
						pass
						# TODO: handel $ cases!
					for i in range(0, int(repeat)):
						dict_delay += int(delay)
						for item in refined_list: 
							prop_cond_dict[counter].append(dict_delay*"X"+item)
			else:
				dict_delay += int(delay)
				for item in refined_list: 
					prop_cond_dict[counter].append(dict_delay*"X"+item)

		if "|->" in line:
			sub_line = line[line.index(">")+1:]
			sumptom = ""
			if "##" in sub_line:
				current_delay = sub_line[sub_line.index("##")+2] 
				symptom =  sub_line[sub_line.index("##")+3:]
			else:
				current_delay = 0
				symptom = sub_line
			signal = (dict_delay + int(current_delay))*"X"+symptom[:symptom.index("==")]
			value = symptom[symptom.index("b")+1:symptom.index(";")]
			prop_symp_dict[counter] = [signal+"["+str(int(log(int(value, 2), 2)))+"]"]
			counter += 1
	prop_file.close()
	print "length of condtion dictionary:", len(prop_cond_dict.keys())
	print "length of symptom dictionary:",len(prop_symp_dict.keys())
	return prop_cond_dict, prop_symp_dict


