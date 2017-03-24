#!/usr/bin/python

import codecs
import json

class UCFEditor:
    """A simple class for editing UCF files.
    
    It is limited in it's scope to modifying repressor parameters and a 
    repressor's on and off thresholds. This feature set is really all that's 
    needed to optimize a Cello run.
    """
    def __init__(self):
        self._JSON_data = []
        self._repressors = {}
        self._source_path = ""

    def load_ucf_from_json(self, path_to_json_file):
        """Import a UCF file from a JSON file on disk."""
        with codecs.open(path_to_json_file, "r", encoding = "utf-8") as data_file:
            self._JSON_data = json.load(data_file)
            self._source_file = path_to_json_file
        for idx, JSON_obj in enumerate(self._JSON_data):
            if "parameters" in JSON_obj:
                self._repressors[JSON_obj["gate_name"]] = idx

    def set_repressor_params(self, repressor_name, values):
        """Set the parameters for a repressor.

        Values should be of the form: (ymax, ymin, K, n, on_threshold, off_threshold)

        Accepts values as a tuple, string, or any other container that can be
        indexed sequentially with integers and square braces.
        """
        if repressor_name in self._repressors:
            repsr = self._JSON_data[self._repressors[repressor_name]]
            params = repsr["parameters"]
            for i in range(4):
                params[i]["value"] = values[i]
            repsr["variables"][0]["off_threshold"] = values[4][1]
            repsr["variables"][0]["on_threshold"] = values[4][0]

    def list_repressors(self):
        """Get a list of all repressors in the file.
        
        Returns a list of strings.
        """
        res = []
        for key in self._repressors:
            res.append(key)
        return res

    def get_repressor_params(self, repressor_name):
        """Get the params for a repressor.
        
        Returns params as a list, of the form [ymax, ymin, K, n, on_threshold, off_threshold]
        """
        repsr = self._JSON_data[self._repressors[repressor_name]]
        params = repsr["parameters"]
        return [params[0]["value"], params[1]["value"], params[2]["value"],
                params[3]["value"], [repsr["variables"][0]["on_threshold"],
                       repsr["variables"][0]["off_threshold"]]]

    def save_ucf_to_json(self, output_path):
        """Pretty-prints the modified json to a file specified by output_path"""
        with codecs.open(output_path, "w", encoding = "utf-8") as data_file:
            json.dump(self._JSON_data, data_file, sort_keys = True, indent = 4, separators = (',', ': '))
