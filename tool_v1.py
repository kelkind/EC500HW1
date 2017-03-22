#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from CelloProvider import CelloConnection
from UCFEditor import UCFEditor
from ToolOperations import *
from ParseResults import *
import numpy as np

  
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
    
    cello.upload_ucf("./" + fname)

    cello.submit_job(jid, gtype, "./Inputs.txt","./Outputs.txt",
                     "options=-UCF testUCF.json -plasmid false -eugene false")

    for result in cello.get_job_results(jid):
        if "logic_circuit.txt" in result.get_name():
            result.download_to_file("./" + rname)

def populate_lists(circuit_tree):
    ed.load_ucf_from_json(fname)
    reps, proms = [], [] 

    for gate in circuit_tree:
        if str(gate) in "Input":
            proms += [gate.get_name()]
        elif str(gate) in ("Nor", "Not"):
            reps += [gate.get_name()]
        
    reps_params = {}
    for gate in reps:
        reps_params[gate] = ed.get_repressor_params(gate)
    rp_copy = reps_params.copy()
    
    proms_params = {}
    for p in proms:
        with open("./Inputs.txt",'r') as inParams:
            for line in inParams:
                if p in line:
                    parts = line.split()
                    proms_params[p] = [parts[1], parts[2]]
                    
    assembly_order = []
    for gate in circuit_tree:
        if isinstance(gate, Output):
            gate.populate_subtree_list(assembly_order)
            
    return assembly_order, proms, reps, proms_params, reps_params, rp_copy

if __name__ == '__main__':
    ed = UCFEditor()
    
    fname, gtype = "testUCF.json", "./0xFE.v"
    uname, pword = "kelkind", "4L83rtO1"
    jid = "KatTest"
    rname = "Results_0xFE_BASE.txt"
    
#    run_Cello(fname, gtype, uname, pword, jid, rname)

    circuit_tree = parse_cello_results_file(rname)

    assembly_order, proms, reps, proms_params, reps_params, rp_copy = populate_lists(circuit_tree)
    
    score = scoreFunction(assembly_order, [proms_params,reps_params])
    print(score)
    
    # preallocates and defines values for the optimization loop
    opsList = ['stretch','incSlope','decSlope','strProm','wkProm','strRBS',
               'wkRBS']
    temp_params, temp_score = {}, {}
    oldScore, maxScoreVal = [score], 0 # initialized as the score to beat

    # optimization loop
    for g in assembly_order: 
        if isinstance(g, Output):
            pass
        elif isinstance(g, Input):
            pass
        else:
            i = 0
            gate = g.get_name()
            print('gate:',gate)
            temp_params[gate], temp_score[gate] = {}, {}
            while maxScoreVal <= oldScore[i-1]:
                for op in opsList:
                    if "stretch" in op:
                        linmax = 1.5
                    elif "Slope" in op:
                        linmax = 1.05
                    else:
                        linmax = 2
                    for sf in np.linspace(0.05,linmax,30):
                        temp_params[gate][op] = modifyGate(reps_params[gate],op,sf)
                        rp_copy[gate] = temp_params[gate][op]
                        temp_score[gate][op] = scoreFunction(assembly_order,
                                  [proms_params,rp_copy])      
                maxScore = max(temp_score[gate], key=lambda key: temp_score[gate][key]) 
                maxScoreVal = temp_score[gate][maxScore]
                if i == 0:
                    break
                if maxScoreVal < oldScore[i-1]:
                    rp_copy[reps[i-1]] = temp_params[reps[i-1]][oldScore]
#            print(temp_score[gate])
#            print(maxScore,':',temp_score[gate][maxScore])
            rp_copy[gate] = temp_params[gate][maxScore] # keeps highest scoring change
            try:
                oldScore[i] = temp_score[gate][maxScore]
            except:
                oldScore += [temp_score[gate][maxScore]]
            i += 1
 
    score = scoreFunction(assembly_order, [proms_params,reps_params])
    print('Final Score:', score)
    
    for gate in reps:    
#        print(gate,":")
#        print(rp_copy[gate])
        ed.set_repressor_params(gate,rp_copy[gate])
        
    fname = "mod" + fname    
    ed.save_ucf_to_json("./" + fname)
    
    rname = "verifyresults" + gtype[:-2] + ".txt"
    run_Cello(fname, gtype, uname, pword, jid, rname)
    
    circuit_tree_new = parse_cello_results_file(rname)

    assembly_order_new, reps_params_new, rp_copy_new, proms_params_new = populate_lists(circuit_tree)
    
    new_score = scoreFunction(assembly_order_new, [proms_params_new,reps_params_new])
    print(new_score)
    
