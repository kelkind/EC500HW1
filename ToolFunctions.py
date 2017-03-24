#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from ParseResults import *
import numpy as np
from ToolOperations import *

def populate_params(circuit_tree, ed):
    """
    populates lists of all of the parameters needed during for optimization
    input: circuit_tree
    output: assembly_order, proms, reps, proms_params, reps_params, rp_copy
    """
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

    return assembly_order, proms, proms_params, reps, reps_params, rp_copy

def optimize(assembly_order, score, proms_params, reps_params, rp_copy,
             change_log):
    opsList = ['stretch','incSlope','decSlope','strProm','wkProm','strRBS',
               'wkRBS']
    temp_params, temp_score = {}, {},
    oldScore, maxScoreVal = [score], 0 
    if change_log != {}:
        CL_n = change_log.copy()
    else:
        CL_n = change_log
    for g in assembly_order: 
        if isinstance(g, Output):
            pass
        elif isinstance(g, Input):
            pass
        else:
            i = 0
            gate = g.get_name()
#            print('gate:',gate)
            temp_params[gate], temp_score[gate] = {}, {}
            while maxScoreVal <= oldScore[i-1]:
                for op in opsList:
#                    print('op:',op)
                    try:
                        if op in change_log[gate]:
                            continue
                    except:
                        pass
                    if "stretch" in op:
                        linmax = 1.5
                    elif "Slope" in op:
                        linmax = 1.05
                    else:
                        linmax = 2
#                    print('calculating...')
                    for sf in np.linspace(0.05,linmax,30):
                        temp_params[gate][op] = modifyGate(reps_params[gate],op,sf)
                        rp_copy[gate] = temp_params[gate][op]
                        temp_score[gate][op] = scoreFunction(assembly_order,
                                  [proms_params,rp_copy])
                        
                maxScore = max(temp_score[gate], key=lambda key: temp_score[gate][key])
                maxScoreVal = temp_score[gate][maxScore]       
#                        
#                currentScores = sorted(temp_score[gate].values(), reverse="True")
#                for op, sc in temp_score[gate].iteritems():
#                    if sc == currentScores[0]:
#                        maxScore = op
                engOps = ["stretch", "incSlope", "decSlope"]
                if maxScore in engOps:
                    subList = temp_score[gate].copy()
                    for item in engOps:
                        del subList[item]
                    secondMax = max(subList, key=lambda key: subList[key])
                    secondMaxVal = subList[secondMax]
                    if maxScoreVal - secondMaxVal < 5:
                        maxScore = secondMax
                        maxScoreVal = secondMaxVal
                CL_n[gate] = maxScore
                if i == 0:
                    break
                if maxScoreVal < oldScore[i-1]:
                    rp_copy[reps[i-1]] = temp_params[reps[i-1]][oldScore]
#            print(maxScore)
#            print(temp_score[gate])
#            print(maxScore,':',temp_score[gate][maxScore])
            rp_copy[gate] = temp_params[gate][maxScore] # keeps highest scoring change
            try:
                oldScore[i] = temp_score[gate][maxScore]
            except:
                oldScore += [temp_score[gate][maxScore]]
            i += 1
    return rp_copy, CL_n