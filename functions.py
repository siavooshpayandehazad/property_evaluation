import sys
import copy
import os

def report_prop_dictonary(prop_dict):
	print "-----------------------------------------------------"
	print "parsed properties:"
	for item in prop_dict.keys():
		print item, "\t",
		for p in prop_dict[item]:
			print p, "\t",
		print 
	return None

def print_help():
	print "This program parses the properties fed in rtf format and generates a testbench for each property"
	print "program arguments:"
	print "\t-i [filename]:	recieves property file in rtf format. Important note, the properties should not use any internal signals!" 
	print "\t-o [filename]:	generated vhdl testbench" 
	return None

def generate_prop_dictionary(prop_file_name):
	print "-----------------------------------------------------"
	print "starting parsing the property file!"
	prop_file = open(prop_file_name, 'r')
	counter = 0
	prop_dict = {}
	for line in prop_file:
		if "G" in line:
			prop =  line.split("->")[0].split("(")[-1].split(")")[0].split("&")
			prop_dict[counter] = copy.deepcopy(prop)
			counter += 1
	print "finished parsing property file... closing file!"
	prop_file.close()
	return prop_dict

def generate_tb(tb_file_name, prop_dictionary):
	initial_file_name = tb_file_name.split(".")[0]

	for prop in prop_dictionary:
		tb_name = "results/"+initial_file_name+"_"+str(prop)+".vhd"
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

		tb_file.write("architecture behavior of multiplier_and_tester_tb is\n\n")
		
		tb_file.write("-- component decleration\n")
		tb_file.write("component breadmaker is\n")
		tb_file.write("prot (\n")

		tb_file.write(");\n")
		tb_file.write("end component;\n\n")
		tb_file.write("signal clk, reset : std_logic := '0';\n")
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

		tb_file.write("    reset <= '1' after 1 ns;\n")
		tb_file.write("\n\n-- instantiate the compoent\n")
		tb_file.write("\nEND;\n")

		print "finished generation of Testbench... closing the file!"
		tb_file.close()
	return None

def parse_arguments(sys_args, package_arguments):
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
	if not os.path.exists("results"):
		os.makedirs("results")
	return None