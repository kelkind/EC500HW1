#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

def checkThresh(inVals, dataIn, table):
    """
    takes the params and checks that the input values are consistent with the
    on and off thresholds and the truth table values
    returns "checks" = 1 or 2,3,4,5. If 1, passed. Otherwise, failed.
    """
    checks = 1
    ymax, ymin, K, n, thresh = dataIn
    for i in range(len(table)):
        if table[i] == 0:
            if inVals[i] < thresh[1]:
                checks += 1                
        elif table[i] == 1:
            if inVals[i] > thresh[0]:
                checks += 1
    return checks

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

def calcValues(dataIn, table, inVals):
    """
    takes repressor params and calculates y values given inVals
    dataIn of the form: [ymax, ymin, K, n, [thresh]]
    table is the on/off table (e.g., [0, 0, 0, 1])
    inVals is a list of numbers at which output value "y" is calculated
    """
    ymax, ymin, K, n, thresh = dataIn
    yvals = [0]* len(table)
    for i in range(len(table)):
        yvals[i] = ymin + (ymax - ymin)/(1 + (inVals[i]/K)**n)
    return yvals

def assemble(gate, params, stored_value):
    """
    Processes each gate according to type:
        Input gate will have its on/off values put in the correct order
        Nor/Not gate will use its input values to calculate the output, and
            verifies the inputs comply with the truth table
        Output gate calculates the score
    Inputs: gate type, [params], {stored gate values}
    It should be used in a for-loop that calls the gates in the proper order.
    See: scoreFunction
    """
    if str(gate) in "Input":
        if gate.get_name() in params[0]:
            vals = params[0][gate.get_name()]
            table = gate.get_table()
            stored_value[gate.get_name()] = []
            for i in table:
                # stores the on/off input values in truth table order
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
            check = checkThresh(inVals, dataIn, table)
            if check == 1:
                stored_value[gate.get_name()] = calcValues(dataIn, table, inVals)
            else:
                stored_value['fail'] = 1
    elif str(gate) in "Output":
        if 'fail' in stored_value.keys():
            score = 0
            return score
        else:
            ipt = gate.get_inputs()
            table = gate.get_table()
            score = calcScore(stored_value[ipt[0].get_name()],table)
            return score
    return stored_value

def scoreFunction(assembly_order, params):
    """
    Takes the assembly order and parameters for each gate/input and passes
    them through the "assemble" function.
    Output is the score of the system
    See: assemble
    """
    stored_value = {}
    for gate in assembly_order:
        if str(gate) in "Output":
            score = assemble(gate, params, stored_value)
        else:
            stored_value = assemble(gate, params, stored_value)
            if 'fail' in stored_value.keys():
                score = 0
                break
    return score

def reportData(dataIn, state, inVals):
    """
    Used to print out all the values computed by a operation function
    """
    ymax, ymin, K, n, thresh = dataIn
    print('ymax:',ymax,'ymin:',ymin)
    print('K:',K,'n:',n)
    print('x_on:',thresh[0],'x_off',thresh[1])
    print('truth table:', state, 'inVals:',inVals)

def modifyGate(dataIn, modtype, scale_factor):
    """
    takes the gate parameters, a scale factor, and the type of modification to
    be performed and applies it. 
    Output is a list of the new parameters.
    Input/Output form: ymax, ymin, K, n, [on_thresh, off_thresh]
    """
    ymax, ymin, K, n, thresh = dataIn
    if modtype == "stretch":
        ymax_new = ymax * scale_factor
        ymin_new = ymin / scale_factor
        thresh_new = calcThresh([ymax_new,ymin_new,K,n])
        dataOut = [ymax_new, ymin_new, K, n, thresh_new]
    elif "Slope" in modtype:
        if modtype == "incSlope":
            n_new = n * scale_factor
        elif modtype == "decSlope":
            n_new = n / scale_factor
        thresh_new = calcThresh([ymax,ymin,K,n_new])
        dataOut = [ymax, ymin, K, n_new, thresh_new]
    elif "Prom" in modtype:
        if modtype == "strProm":
            ymax_new = ymax * scale_factor
            ymin_new = ymin * scale_factor
        elif modtype == "wkProm":
            ymax_new = ymax / scale_factor
            ymin_new = ymin / scale_factor
        thresh_new = calcThresh([ymax_new,ymin_new,K,n])
        dataOut = [ymax_new, ymin_new, K, n, thresh_new]
    elif "RBS" in modtype:
        if modtype == "strRBS":
            K_new = K / scale_factor
        elif modtype == "wkRBS":
            K_new = K * scale_factor
        thresh_new = calcThresh([ymax,ymin,K_new,n])
        dataOut = [ymax, ymin, K_new, n, thresh_new]
    return dataOut
