#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from CelloProvider import CelloConnection
from UCFEditor import UCFEditor
from ParseResults import *
from ToolOperations import *
from ToolFunctions import *
import sys, getopt
  
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
#
#def main(argv):
#    """
#    Main Argument
#    """
#    
#    if len(argv) == 1:
#        help_Script()
#    elif len(argv) == 2:
#        if argv[1] == "-version":
#            print("Optron version: 1.0")
#            sys.exit()
#        if argv[1] == "-help":
#            help_Script()
#            
#    else:
#        try:
#            opts, args = getopt.getopt(argv[1:],"",["username="
#                                       "password=","ucf=","verilog=","jobid=",
#                                       "results="])
#        except getopt.GetoptError:
#            print("try Optron.py -help for a list of valid commands")
#            sys.exit()
#    print(opts)
#    print(args)
#    for opt, arg in opts:
#        if opt in "-version":
#            print("Optron version: 1.0")
#            sys.exit()
#        elif opt in "-username":
#            uname = arg
#        elif opt in "-password":
#            pword = arg
#        elif opt in "-ucf":
#            if arg.endswith(".UCF.json"):
#                UCFname = arg
#            else:
#                print("Invalid UCF filename. Filename must end with '.UCF.json'") 
#                sys.exit()
#        elif opt in "-verilog":
#            vFile = arg
#        elif opt in "-jobid":
#            jobID = arg
#        elif opt in "-results":
#            if ".txt" in arg:
#                resultsFile = arg
#            else:
#                resultsFile = arg + ".txt"
#        else:
#            help_Script()
#    # check for optional outputs:
#    try:
#        jobID
#    except:
#        jobID = UCFname[:-9]
#    try:
#        resultsFile
#    except:
#        resultsFile = UCFname[:-9] + ".txt"
#    
#    return uname, pword, UCFname, vFile, jobID, resultsFile

def usage():
    print("Welcome to Optron, the Cello Optimization Tool")
    print("Usage: Optron.py [OPTIONS] [ARGUMENTS]\n")
    print("-------")
    print("Options")
    print("-------\n")
    print("-version       print version and exit")
    print("-help          show this message and exit")
    print("-username      Cello Username")
    print("-password      Cello Password")
    print("-ucf           UCF file to be used by Cello")
    print("-verilog       Verilog file of logic circuit")
    print("-jobid         Job ID in Cello (optional)")
    print("-results       name of text file to save Cello results (optional)\n")
    sys.exit(2)
	
def verify_no_required_opts_missing(parsed_fields):
    for key in parsed_fields:
        if not parsed_fields[key]:
            print("Error, missing required parameter: " + key)
            usage()

def parse_opts():
    results = {
        "name": None,
        "password": None,
        "ucf": None,
        "verilog": None,
        "jobid": "OptronRun",
        "results": "OptronResults.txt"
        }
    for o, a in opts:
        if o in ("-n", "--name"):
            results["name"] = a
        elif o in ("-p", "--password"):
            results["password"] = a
        elif o in ("-u", "--ucf"):
            results["ucf"] = a
        elif o in ("-v", "--verilog"):
            results["verilog"] = a
        elif o in ("-j", "--jobid"):
            results["jobid"] = a
        elif o in ("-r", "--results"):
            results["results"] = a
    verify_no_required_opts_missing(results)
    return results

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "n:p:u:v:j:r:", ["name=", "password=", "ucf=", "verilog=", "jobid=", "results="])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
    opt_data = parse_opts()
    for key in opt_data:
        if key in "name":
            uname = opt_data[key]
        elif key in "password":
            password = opt_data[key]
        elif key in "ucf":
            UCFname = opt_data[key]
            while UCFname.endswith(".UCF.json") == 0:
                print("Invalid UCF filename! Filename must end with '.UCF.json'")
                UCFname = raw_input("Enter valid UCF file name: ")
        elif key in "verilog":
            vFile = opt_data[key]
            if vFile.startswith("./") == 0:
                vFile = "./" + vFile
        elif key in "jobid":
            jobID = opt_data[key]
        elif key in "results":
            resultsFile = opt_data[key]
            if resultsFile.endswith(".txt") == 0:
                resultsFile = resultsFile + ".txt"
                
    ed = UCFEditor()

#    print('name',uname)
#    print('pw',password)
#    print('ucf',UCFname)
#    print('veri',vFile)
#    print('job',jobID)
#    print('res',resultsFile)

    
    run_Cello(UCFname, vFile, uname, password, jobID, resultsFile)

    circuit_tree = parse_cello_results_file(resultsFile)

    ed.load_ucf_from_json(UCFname)
    
    assembly_order, proms, proms_params, reps, reps_params, rp_copy = \
        populate_params(circuit_tree, ed)

    score = scoreFunction(assembly_order, [proms_params,reps_params])
    print('Your initial score is ' + str(score))

    # optimizes the solution
    change_log = {}
    rp_copy, change_log = optimize(assembly_order, score, proms_params,
                                   reps_params, rp_copy, change_log)

    # calculates and prints the score of the optimized function
    opt_score = scoreFunction(assembly_order, [proms_params,rp_copy])
    
    for gate in reps:    
        ed.set_repressor_params(gate,rp_copy[gate])
    
    ed.save_ucf_to_json("./" + UCFname)
    
    resultsFile = "verifyresults" + vFile[2:-2] + ".txt"
    jobID = jobID + "1"
    run_Cello(UCFname, vFile, uname, password, jobID, resultsFile)
    
    circuit_tree_new = parse_cello_results_file(resultsFile)

    assembly_order_n, proms_n, proms_params_n, reps_n, reps_params_n, \
        rp_copy_n = populate_params(circuit_tree_new, ed)

    new_score = scoreFunction(assembly_order_n, [proms_params_n, reps_params_n])
#    print(new_score)
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
        new_score = scoreFunction(assembly_order_n, [proms_params,rp_copy_n])
#        print(scoreFunction(assembly_order_n, [proms_params,rp_copy_n]))
        
#    print(change_log_n)
    print(new_score)
    print('Your Optimized Score is ' + str(new_score))
    print('Using the Following Changes:')
    for key in change_log:
        print(str(key) + ": " + change_log[key])
    print('See your modified UCF file for details.')