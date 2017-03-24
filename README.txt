README.txt

--------------
Included Files
--------------

OptronTool.py
Operations.py
OptronFns.py
ParseResults.py
CelloProvider.py
UCFEditor.py


-----------------
Required Software
-----------------

Python (v3.5.2 or later)
Numpy  (v1.12.1)


—--------------
Install and Run
---------------

1) Unzip files to a local directory
2) In terminal, navigate to that directory
3) Add all files that will be used to the directory. This includes files that are necessary for Cello to run properly: 
Inputs.txt, Outputs.txt, verilog file, UCF file
3) Type: python OptronTool.py


----------------------
Command Line Arguments
----------------------

Example:  python OptronTool.py --name "TStark" --password “IAmIronMan” --ucf “myUCF.UCF.json” --verilog “AND.v” --results “resultsFile.txt” 

--name (-n)		(required) Cello username

--password (-p) 	(required) Cello password

--ucf (-u)		(required) UCF file. Must be in local directory.

--verilog (-v)		(required) Verilog file. Must be in local directory.

—-jobid (-j)		(optional) Cello Job ID. If --jobid is omitted, ucf
				file name is used (e.g., “myUCF”).

--results (-r)		(optional) txt file to store results. If --results is 					
				omitted, “myUCF.results.txt” is used


--version		Posts current version

—help			Shows usage details.


