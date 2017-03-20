#!/usr/bin/python

from collections import deque

class Gate:
    def __init__(self):
        self._name = ""
        self._truth_table = []
        self._inputs = []
        self._outputs = []

    def get_inputs(self):
        return self._inputs

    def get_name(self):
        return self._name

    def get_outputs(self):
        return self._outputs

    def get_table(self):
        return self._truth_table

    def set_name(self, name):
        self._name = name

    def set_table(self, table):
        self._truth_table = table

    def populate_subtree_list(self, lst):
        for gate in self._inputs:
            gate.populate_subtree_list(lst)
        lst.append(self)

class Input(Gate):
    def __repr__(self):
        return "Input"


class Output(Gate):
    def set_inputs(self, inputs):
        if len(inputs) != 1:
            raise RuntimeError("Wrong number of inputs for Output")
        self._inputs = inputs

    def __repr__(self):
        return "Output"


class Not(Gate):
    def set_inputs(self, inputs):
        if len(inputs) != 1:
            raise RuntimeError("Wrong number of inputs for Not")
        self._inputs = inputs

    def __repr__(self):
        return "Not"

class Nor(Gate):
    def set_inputs(self, inputs):
        if len(inputs) != 2:
            raise RuntimeError("Wrong number of inputs for Nor")
        self._inputs = inputs

    def __repr__(self):
        return "Nor"

def get_file_as_string(path):
    with open(path) as file_data:
        content = file_data.read()
    return content

def seek_logic_circuit(lines):
    while lines and not "Logic Circuit" in lines[0]:
        lines.popleft()
    if lines:
        lines.popleft()

def parse_truth_table(table_as_string):
    truth_table = []
    ASCII_ZERO = 48
    for char in table_as_string:
        truth_table.append(ord(char) - ASCII_ZERO)
    return truth_table

def parse_inputs_list(strrep):
    csv = strrep.strip("()")
    values = csv.split(",")
    return values

def parse_logic_circuit(lines, gates):
    while lines and not "Circuit_score" in lines[0]:
        tokens = lines[0].split()
        if tokens:
            gate = {
                "OUTPUT": Output(),
                "NOT": Not(),
                "NOR": Nor(),
                "INPUT": Input(),
            }[tokens[0]]
            if not "INPUT" in tokens[0]:
                gate.set_inputs(parse_inputs_list(tokens[4]))
            gate.set_name(tokens[2])
            gate.set_table(parse_truth_table(tokens[1]))
            gates[tokens[3]] = gate
        lines.popleft()

def dfs_link_outputs(current_node):
    for gate in current_node.get_inputs():
        gate._outputs.append(current_node)
        dfs_link_outputs(gate)

def construct_netlist_tree(gates_map):
    tree = []
    for key in gates_map:
        tree.append(gates_map[key])
        for i in range(len(gates_map[key]._inputs)):
            gates_map[key]._inputs[i] = gates_map[gates_map[key]._inputs[i]]
    for gate in tree:
        if isinstance(gate, Output):
            dfs_link_outputs(gate)
    return tree

def parse_cello_results_file(path):
    lines = deque(get_file_as_string(path).split("\n"))
    gates = {}
    while lines:
        seek_logic_circuit(lines)
        if lines:
            parse_logic_circuit(lines, gates)
    return construct_netlist_tree(gates)

def print_via_depth_first_traversal(gate, indentation):
    print(" " * indentation + str(gate))
    print(" " * indentation + gate.get_name())
    print(" " * indentation + str(gate.get_table()))
    for child in gate.get_inputs():
        print_via_depth_first_traversal(child, indentation + 2)

def print_via_depth_reverse(gate, indentation, count):
    print(" " * indentation + str(gate))
    print(" " * indentation + gate.get_name())
    print(" " * indentation + str(gate.get_table()))
    for child in gate.get_outputs():
        if len(child.get_inputs()) <= count:
            print_via_depth_reverse(child, indentation + 2, count)
        else:
            break