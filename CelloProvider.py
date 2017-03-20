#!/usr/bin/python

import requests
import json
import ntpath

_cello_url = "http://cellocad.org:8080"

class CelloConnectionError(Exception):
        def __init__(self):
                self.message = "Cello connection refused"

class CelloResultHandle:
        def __init__(self, file_name, job_name, connection):
                self._file_name = file_name
                self._job_name = job_name
                self._connection = connection

        def get_name(self):
                return self._file_name

        def download_to_file(self, file_name):
                r = requests.get(_cello_url + "/results/" +
                                 self._job_name + "/" + self._file_name,
                                 auth = self._connection._auth)
                if r.status_code != 200:
                        raise CelloConnectionError()
                f = open(file_name, "w")
                f.write(r.text)
                f.close()

        
class CelloConnection:
        def __init__(self, auth):
                self._auth = auth

        def upload_ucf(self, file_path):
                upload_name = ntpath.basename(file_path)
                if not upload_name:
                        raise CelloConnectionError()
                with open(file_path, "r") as content_file:
                        content = content_file.read()
                        r = requests.post(_cello_url + "/ucf/" + upload_name,
                                          auth = self._auth,
                                          data = {"filetext": content})
                        if r.status_code != 200:
                                raise CelloConnectionError()
                        r = requests.get(_cello_url + "/ucf/" + upload_name + "/validate",
                                         auth = self._auth)
                if r.status_code != 200:
                        raise CelloConnectionError()
                resultsJSON = json.loads(r.text)
                if resultsJSON["status"] != "VALID":
                        raise RuntimeError("UCF validation failed")

        def delete_ucf(self, ucf_file_name):
                r = requests.delete(_cello_url + "/ucf/" + ucf_file_name,
                                    auth = self._auth)
                if r.status_code != 200:
                        raise CelloConnectionError()
                
        def netsynth(self, file_path):
                with open(file_path, "r") as content_file:
                        content = content_file.read()
                        r = requests.post(_cello_url + "/netsynth",
                                          auth = self._auth,
                                          data = {"verilog_text": content})
                        if r.status_code != 200:
                                CelloConnectionError()
                        return r.text

        def submit_job(self,
                       job_name,
                       verilog_path,
                       promoter_path,
                       outputs_path,
                       opt_str = ""):
                with open(verilog_path, "r") as v, open(promoter_path, "r") as p, open(outputs_path, "r") as o:
                        v_content = v.read()
                        p_content = p.read()
                        o_content = o.read()
                        r = requests.post(_cello_url + "/submit",
                                          auth = self._auth,
                                          data = {"id": job_name,
                                                  "verilog_text": v_content,
                                                  "input_promoter_data": p_content,
                                                  "output_gene_data": o_content,
                                                  "options": opt_str})
                        if r.status_code != 200:
                                raise CelloConnectionError()

        def delete_job(self, job_name):
                r = requests.delete(_cello_url + "/results/" + job_name,
                                    auth = self._auth)
                if r.status_code != 200:
                        raise CelloConnectionError()

        def get_job_results(self, job_name):
                r = requests.get(_cello_url + "/results/" + job_name,
                                 auth = self._auth);
                if r.status_code != 200:
                        raise CelloConnectionError()
                resultsJSON = json.loads(r.text)
                results = []
                for fname in resultsJSON["files"]:
                        results.append(CelloResultHandle(fname, job_name, self))
                return results
