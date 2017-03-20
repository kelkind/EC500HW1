#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

def calcThresh(dataIn):
    """
    takes a list of params and calculates new x_on and x_off thresholds
    thresholds. returns a list
    list of the form: (ymax ymin K n [thresh])
    """
    ymax, ymin, K, n = dataIn
    x_on = K * ((ymax - 2*ymin)/(2*ymin - ymin))**(1/n)
    x_off = K * ((ymax - ymax/2)/(ymax/2 - ymin))**(1/n)
    thresh = [x_on, x_off]
    return thresh

def calcScore(yvals,table):
    """
    takes a list of lists of the output values and calculates the new score
    for the repressor
    yvals of the form: [[val1 val2 val3], [val4]] if table is (0 0 0 1)
    """
    onVals, offVals = [],[]
    for i in range(len(yvals)):
        if table[i] == 1:
            onVals += [yvals[i]]
        else:
            offVals += [yvals[i]]
    on_min = min(onVals) # find the minimum "on" value
    off_max = max(offVals) # find the maximum "off" value
    score = on_min / off_max
    return score

def calcValues(dataIn, state, inVals):
    """
    takes a list of params and calculates input and output values for the
    repressor.
    dataIn of the form: (ymax ymin K n [thresh])
    state is the on/off state matrix (i.e. 0 0 0 1)
    inVals is a list of numbers at which output value "y" is calculated
    """
    ymax, ymin, K, n, thresh = dataIn
    yvals = [0,0,0,0]
    for i in range(4):
        yvals[i] = ymin + (ymax - ymin)/(1 + (inVals[i]/K)**n)
    return yvals


def assemble(gate, params, stored_value):
    if str(gate) in "Input":
        if gate.get_name() in params[0]:
            vals = params[0][gate.get_name()]
            table = gate.get_table()
            stored_value[gate.get_name()] = []
            for i in table:
                # this should store the on/off values in truth table order
                stored_value[gate.get_name()] += [vals[i]]
    elif str(gate) in ("Not","Nor"):
        inVals = []
        if gate.get_name() in params[1]:
            gateInputs = gate.get_inputs()
            iptNames = []
            for ipt in gateInputs:
                iptNames += [ipt.get_name()]
            if len(iptNames) == 1:
                inVals = stored_value[iptNames[0]]
            else:
                inV1 = stored_value[iptNames[0]]
                inV2 = stored_value[iptNames[1]]
                inVals = [x + y for x, y in zip(inV1,inV2)]
            for i in range(len(inVals)):
                inVals[i] = float(inVals[i])
            table = gate.get_table()
            dataIn = params[1][gate.get_name()]
            stored_value[gate.get_name()] = calcValues(dataIn, table, inVals)
    elif str(gate) in "Output":
        ipt = gate.get_inputs()
        table = gate.get_table()
        score = calcScore(stored_value[ipt[0].get_name()],table)
        return score
    return stored_value


def reportData(dataIn, state, inVals):
    """
    Used to print out all the values computed by a operation function
    """
    ymax, ymin, K, n, thresh = dataIn
    print('ymax:',ymax,'ymin:',ymin)
    print('K:',K,'n:',n)
    print('x_on:',thresh[0],'x_off',thresh[1])
    print('truth table:', state, 'inVals:',inVals)

def stretch(dataIn, scale_factor):
    """
    takes a list of params and applies "stretch" function
    lists of the form: (ymax ymin K n [thresh])
    state is the on/off state matrix (i.e. 0 0 0 1)
    inVals is a list of the values at which value "y" is calculated
    """
#    dataOut = dataIn
    ymax, ymin, K, n, thresh = dataIn
#    score = calcScore(dataIn, state, inVals)
#    for val in np.linspace(0.05,1.5,num=30):
    ymax_new = ymax * scale_factor
    ymin_new = ymin / scale_factor
    thresh_new = calcThresh([ymax_new,ymin_new,K,n])
#    score_new = calcScore([ymax_new,ymin_new,K,n,thresh_new], state, inVals)
#        print('ymax:',ymax_new,'ymin:',ymin_new)
#        print('x_on:',thresh_new[0],'x_off',thresh_new[1])
#        print('score_old:',score,'score_new',score_new)
#        print('')
#        if score_new > score:
#            dataOut[0],dataOut[1],dataOut[4] = ymax_new,ymin_new,thresh_new
    dataOut = [ymax_new, ymin_new, K, n, thresh_new]
    return dataOut

def changeSlope(dataIn, IorD, scale_factor):
    """
    takes a list of params and changes the slope
    list of the form: (ymax ymin K n [thresh])
    state is the on/off state matrix (i.e. 0 0 0 1)
    inVals is a list of the values at which value "y" is calculated
    IorD is a character 'i' or 'd', indicates increase or decrease
    """
#    dataOut = dataIn
    ymax, ymin, K, n, thresh = dataIn
#    score = calcScore(dataIn, state, inVals)
#    for val in np.linspace(1.005,1.05,num=10):
    if IorD == 'i':
        n_new = n * scale_factor
    else:
        n_new = n / scale_factor
    thresh_new = calcThresh([ymax,ymin,K,n_new])
#        score_new = calcScore([ymax,ymin,K,n_new,thresh_new], state, inVals)
#        if score_new > score:
#            dataOut[3], dataOut[4] = n_new, thresh_new
    dataOut = [ymax, ymin, K, n_new, thresh_new]
    return dataOut

def Prom(dataIn, SorW, scale_factor):
    """
    takes a list of params and makes the promoter stronger or weaker
    list of the form: (ymax ymin K n [thresh])
    state is the on/off state matrix (i.e. 0 0 0 1)
    inVals is a list of the values at which value "y" is calculated
    SorW is a character 's' or 'w', indicates strong or weak
    """
#    dataOut = dataIn
    ymax, ymin, K, n, thresh = dataIn
#    score = calcScore(dataIn, state, inVals)
#    for val in np.linspace(0,10,num=20):
    if SorW == 's':
        ymax_new = ymax * scale_factor
        ymin_new = ymin * scale_factor
    else:
        ymax_new = ymax / scale_factor
        ymin_new = ymin / scale_factor
    thresh_new = calcThresh([ymax_new,ymin_new,K,n])
#        score_new = calcScore([ymax_new,ymin_new,K,n,thresh_new], state, inVals)
#        if score < score_new:
#            dataOut[0],dataOut[1],dataOut[4] = ymax_new,ymin_new,thresh_new
    dataOut = [ymax_new, ymin_new, K, n, thresh_new]
    return dataOut

def RBS(dataIn, SorW, scale_factor):
    """
    takes a list of params and makes the RBS stronger or weaker
    list of the form: (ymax ymin K n [thresh])
    state is the on/off state matrix (i.e. 0 0 0 1)
    inVals is a list of the values at which value "y" is calculated
    SorW is a character 's' or 'w', indicates strong or weak
    """
#    dataOut = dataIn
    ymax, ymin, K, n, thresh = dataIn
#    score = calcScore(dataIn, state, inVals)
#    for val in np.linspace(0,10,num=20):
    if SorW == 's':
        K_new = K / scale_factor
    else:
        K_new = K * scale_factor
    thresh_new = calcThresh([ymax,ymin,K_new,n])
#        score_new = calcScore([ymax,ymin,K_new,n,thresh_new], state, inVals)
#        if score < score_new:
#            dataOut[2], dataOut[4] = K_new, thresh_new
    dataOut = [ymax, ymin, K_new, n, thresh_new]
    return dataOut