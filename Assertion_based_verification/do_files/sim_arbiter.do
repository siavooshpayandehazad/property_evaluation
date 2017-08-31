#---------------------------------------------
#-- THIS FILE IS GENERATED AUTOMATICALLY    --
#--           DO NOT EDIT                   --
#---------------------------------------------

rm -rf results/ 
mkdir results

# Include files and compile them
vlog -work work  "state_defines.v"
vlog -work work  "parameters.v"
vlog -work work -cover bcesfx -vopt +incdir+ -cover bcesfx "arbiter.v"
vlog -sv "arbiter_tb.sv"

# Start the simulation
vsim -assertdebug -coverage -voptargs="+cover=bcestfx" work.arbiter_tb

# View Assertions
view assertions

# Run the simulation
run -all

# save the coverage reports
coverage save results/coverage_arbiter.ucdb

vcover report -assert -detail -output results/assertion_report_det.txt results/coverage_arbiter.ucdb

# Exit Modelsim after simulation
exit