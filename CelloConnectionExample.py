#!/usr/bin/python

from CelloProvider import CelloConnection

cello = CelloConnection(("evan_bowman", "eb05270618"))

cello.upload_ucf("./gates_Eco1C1G1T1.json")

cello.submit_job("my-cello-test", "./AND.v", "./Inputs.txt", "./Outputs.txt",
                 "options=-UCF gates_Eco1C1G1T1.json -plasmid false -eugene false")

for result in cello.get_job_results("my-cello-test"):
	if "logic_circuit.txt" in result.get_name():
		result.download_to_file("./results.txt")

cello.delete_ucf("gates_Eco1C1G1T1.json")

cello.delete_job("my-cello-test")