#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from CelloProvider import CelloConnection
from UCFEditor import UCFEditor
from ParseResults import *
from ToolOperations import *
from ToolFunctions import *
import sys
#import numpy as np

  
def get_user_inputs():
    """
    Prompt to provide all of their user and file information to run Cello.
    Asks for: UCF file name, Verilog File name, Cello Username, Cello Password
    Job ID, and Results File (where to store results)
    """
    UCFname = raw_input('UCF file name: ') # gets user input
    vFile = raw_input('Verilog File: ') # gets gate type (AND, etc.)
    if ".v" not in vFile:
        vFile += ".v"
    if "/" not in vFile:
        vFile = "./" + vFile
    uname = raw_input('Cello Username: ') # gets username
    pword = raw_input('Cello Password: ') # gets password
    jobID = raw_input('Define Job ID: ') # gets new job ID
    resultsFile = raw_input('Results File Name: ') # gets filename to store results
    if ".txt" not in resultsFile:
        resultsFile += ".txt" 
    return UCFname, vFile, uname, pword, jobID, resultsFile

def run_Cello(UCFname, vFile, uname, pword, jobID, resultsFile):
    """
    Uploads the current UCF file, runs Cello, and downloads the logic circuit
    Input: UCF file name, Circuit Type, Username, Password, Job ID, and
        results file name.
    """
    cello = CelloConnection((uname, pword))
    
    cello.delete_ucf(UCFname)
    cello.upload_ucf("./" + UCFname)

    ops = "-UCF " + UCFname + " -plasmid false -eugene false"
    cello.submit_job(jobID, vFile, "./Inputs.txt","./Outputs.txt", ops)

    for result in cello.get_job_results(jobID):
        if "logic_circuit.txt" in result.get_name():
            result.download_to_file("./" + resultsFile)


if __name__ == '__main__':
    if len(sys.argv)==1 or sys.argv[1]=="--help":
        print("Welcome to Optron, the Cello Optimization Tool")
        print("Usage: Optron.py [OPTIONS] [ARGUMENTS]\n")
        print("-------")
        print("Options")
        print("-------\n")
        print("--version       print version and exit")
        print("--help          show this message and exit")
        print("--username      Cello Username")
        print("--password      Cello Password")
        print("--ucf           UCF file to be used by Cello")
        print("--results       name of text file to save Cello results\n")
        sys.exit()
    elif sys.argv[1]=="--version":
        print("Optrion version: 1.0")
        sys.exit()
    else:
        if "username" in sys.argv:
            uname = sys
    UCFname, vFile, uname, pword, jobID, resultsFile = get_user_inputs()
    
    ed = UCFEditor()
    
    UCFname = "testUCF.UCF.json"
    vFile = "./0xFE.v"
    uname = "kelkind"
    pword = "4L83rtO1"
    jobID = "Kat_Evan_Test"
    resultsFile = "Results_0xFE.txt"
    
#    run_Cello(UCFname, vFile, uname, pword, jobID, resultsFile)

    circuit_tree = parse_cello_results_file(resultsFile)

    ed.load_ucf_from_json(UCFname)
    
    assembly_order, proms, proms_params, reps, reps_params, rp_copy = \
        populate_params(circuit_tree, ed)

    score = scoreFunction(assembly_order, [proms_params,reps_params])
    print(score)

    # optimizes the solution
    change_log = {}
    rp_copy, change_log = optimize(assembly_order, score, proms_params,
                                   reps_params, rp_copy, change_log)

    # calculates and prints the score of the optimized function
    opt_score = scoreFunction(assembly_order, [proms_params,rp_copy])
    print('Final Score:', opt_score)
    
    for gate in reps:    
#        print(gate,":")
#        print(rp_copy[gate])
        ed.set_repressor_params(gate,rp_copy[gate])
    
    ed.save_ucf_to_json("./" + UCFname)
    
    resultsFile = "verifyresults" + vFile[2:-2] + ".txt"
    jobID = jobID + "1"
#    run_Cello(UCFname, vFile, uname, pword, jobID, resultsFile)
    
    circuit_tree_new = parse_cello_results_file(resultsFile)

    assembly_order_n, proms_n, proms_params_n, reps_n, reps_params_n, \
        rp_copy_n = populate_params(circuit_tree_new, ed)

    new_score = scoreFunction(assembly_order_n, [proms_params_n, reps_params_n])
    print(new_score)
#    print(change_log)
    if new_score > opt_score:
        opsList = ['stretch','incSlope','decSlope','strProm','wkProm','strRBS',
               'wkRBS']
        old = []
        for key in change_log.keys():
            if key not in reps_n:
                old += [key]
        for r in old:
            del change_log[r]
        rp_copy_n, change_log_n = optimize(assembly_order_n, opt_score,
                                           proms_params_n, reps_params_n,
                                           rp_copy_n, change_log)
        print(scoreFunction(assembly_order_n, [proms_params,rp_copy_n]))
        
#    print(change_log_n)