#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from CelloProvider import CelloConnection
from UCFEditor import UCFEditor
from ToolOperations import *
from ParseResults import *

  
def get_user_inputs():
    fname = input('UCF file name: ') # gets user input
    gtype = input('Verilog File for Gate Type: ') # gets gate type (and, etc.)
    if ".v" not in gtype:
        gtype += ".v"
    if "/" not in gtype:
        gtype = "./" + gtype
    uname = input('Cello Username: ') # gets username
    pword = input('Cello Password: ') # gets password
    jid = input('Define Job ID: ') # gets new job ID
    rname = input('Results File Name: ') # gets filename to store results
    if "." not in rname:
        rname += ".txt" 
    return fname, gtype, uname, pword, jid, rname

def run_Cello(fname, gtype, uname, pword, jid, rname):
    cello = CelloConnection((uname, pword))
    
#    cello.upload_ucf("./testUCF.json")
#
#    cello.submit_job(jid, gtype, "./Inputs.txt","./Outputs.txt",
#                     "options=-UCF testUCF.json -plasmid false -eugene false")

    for result in cello.get_job_results(jid):
        if "logic_circuit.txt" in result.get_name():
            result.download_to_file("./" + rname)

def score_function(assembly_order, params):
    stored_value = {}
    for gate in assembly_order:
        if str(gate) in "Output":
            score = assemble(gate, params, stored_value)
        else:
            stored_value = assemble(gate, params, stored_value)
    return score

if __name__ == '__main__':
    ed = UCFEditor()
    circuit_tree = parse_cello_results_file("resultsTesting.txt")


    fname = "testUCF.json"
    gtype = "./AND.v"
    uname = "kelkind"
    pword = "4L83rtO1"
    jid = "KatTest"
    rname = "resultsTesting.txt"
    
    run_Cello(fname, gtype, uname, pword, jid, rname)

#    parse the results file, get:
    reps, proms = [], [] 

    for gate in circuit_tree:
        if str(gate) in "Input":
            proms += [gate.get_name()]
        elif str(gate) in ("Nor", "Not"):
            reps += [gate.get_name()]
    
#    count = 1
#    for gate in circuit_tree: 
##        if isinstance(gate, Output):
##            print_via_depth_first_traversal(gate, 0)
#        numInputs = len(proms)
#        if isinstance(gate, Input):
#            print_via_depth_reverse(gate, 0, count)
#            count += 1
#        
    ed.load_ucf_from_json(fname)

    reps_params = {}
    for gate in reps:
        reps_params[gate] = ed.get_repressor_params(gate)
    
    proms_params = {}
    for p in proms:
        with open("./Inputs.txt",'r') as inParams:
            for line in inParams:
                if p in line:
                    parts = line.split()
                    proms_params[p] = [parts[1], parts[2]]

#   calculate score 
#    stored_value = {}
    assembly_order = []
    for gate in circuit_tree:
        if isinstance(gate, Output):
            gate.populate_subtree_list(assembly_order)
#            assembly_order += [gate.get_value()]
    print(assembly_order)
    
    score = score_function(assembly_order, [proms_params,reps_params])
    print(score)    
    
#    for gate in reps:
#        for sf in np.linspace(0.05,1.5,20):
#            reps_params[gate] = stretch(reps_params[gate],sf)
#            adj_score = assemble("Output",[proms_params,reps_params],
#                                 s_value)
#            if adj_score > score:
#                pass

    
#            stored_value = run_start_to_finish(gate,[proms_params,reps_params],
#                                               stored_value)
                

    # set the parameters for a repressor, parameter can be a list, etc
#    ed.set_repressor_params(repsrs_list[0], [99, 99, 99, 99])

#    ed.save_ucf_to_json("testUCFedited.json")
    
    # data for P3_PhlF
#    dataIn = [6.8, 0.02, .23, 4.2, [0.920133536,0.230323307]]
#    state = [0, 0, 0, 1]
#    inVals = [2.100 + 3.683, 2.1 + 0.072, .003 + 3.683, .003 + .072]
#    print('Initial Values for P3_PhlF:')
#    TO.reportData(dataIn, state, inVals)
#    
#    print('\nStretch:')
#    dataOut = TO.stretch(dataIn, state, inVals)
#    TO.reportData(dataOut, state, inVals)
#    score = TO.calcScore(dataOut, state, inVals)
#    print('score:',score)
#
#    dataIn = [6.8, 0.02, .23, 4.2, [0.920133536,0.230323307]]
#
#    print('\nIncrease Slope:')
#    dataOut = TO.changeSlope(dataIn, state, inVals, 'i')
#    TO.reportData(dataOut, state, inVals)
#    score = TO.calcScore(dataOut, state, inVals)
#    print('score:',score)
#    
#    dataIn = [6.8, 0.02, .23, 4.2, [0.920133536,0.230323307]]
#
#
#    print('\nStrong Promoter:')
#    dataOut = TO.Prom(dataIn, state, inVals, 's')
#    TO.reportData(dataOut, state, inVals)
#    score = TO.calcScore(dataOut, state, inVals)
#    print('score:',score)
# 
#    dataIn = [6.8, 0.02, .23, 4.2, [0.920133536,0.230323307]]
#
#    print('\nWeak RBS')
#    dataOut = TO.RBS(dataIn, state, inVals, 'w')
#    TO.reportData(dataOut, state, inVals)
#    score = TO.calcScore(dataOut, state, inVals)
#    print('score:',score)
