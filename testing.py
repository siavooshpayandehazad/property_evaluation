# Copyright (C) 2017 Siavoosh Payandeh Azad and Tsotne Putkaradze
# License: GNU GENERAL PUBLIC LICENSE Version 3
import sys


def test_prop_cond_dict(prop_cond_dict):
	for item in prop_cond_dict.keys():
		if isinstance(prop_cond_dict[item], list):
			for sub_item in prop_cond_dict[item]:
				if not isinstance(sub_item, str):
					return False
		else:
			return False
	return True


def test_prop_symp_dict(prop_symp_dict):
	for item in prop_symp_dict.keys():
		if isinstance(prop_symp_dict[item], list):
			for sub_item in prop_symp_dict[item]:
				if not isinstance(sub_item, str):
					return False
		else:
			return False
	return True


def test_prop_dicts(prop_cond_dict,prop_symp_dict):
	print "----------------------------------------------"
	print "starting testing..."
	if not test_prop_cond_dict(prop_cond_dict):
		print "=>    prop_cond_dict test faild..."
		sys.exit()
	else:
		print "=>    prop_cond_dict test passed..."

	if not test_prop_symp_dict(prop_symp_dict):
		print "=>    prop_symp_dict test faild..."
		sys.exit()
	else:
		print "=>    prop_symp_dict test passed..."
	return None
