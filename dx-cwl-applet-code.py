import os
import dxpy
import json
import yaml
import subprocess
from pprint import pprint

def sh(cmd, ignore_error=False):
    try:
        print cmd
        subprocess.check_call(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        if ignore_error:
            return
        else:
            sys.exit(e.returncode)

def shell_suppress(cmd, ignore_error=False):
    out = ""
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        if ignore_error:
            pass
        else:
            print e.output
            raise
    return out

@dxpy.entry_point('main')
def main(**kwargs):
    print "Installing custom cwltool"
    sh("pip install -U pip wheel setuptools")
    sh("cd cwltool/ && python setup.py install > /dev/null 2>&1 && cd ..")
    sh("cd cwltool/cwlref-runner && python setup.py install > /dev/null 2>&1 && cd ../../")
    sh("curl https://nodejs.org/dist/v6.11.2/node-v6.11.2-linux-x64.tar.gz | tar xzvf - --strip-components 1 -C /usr/local/ > /dev/null")

    print("Download inputs and create CWL file")
    with open("job_input.json") as f:
        dxinputs = json.loads(f.read())

    tool = yaml.load(open("tool.cwl").read())
    if isinstance(tool['inputs'], list):
        tool['inputs'] = {i['id']:i for i in tool['inputs']}
    if isinstance(tool['outputs'], list):
        tool['outputs'] = {i['id']:i for i in tool['outputs']}
    pprint(tool)


    def is_file(ivalue):
        return isinstance(ivalue, dict) and ('$dnanexus_link' in ivalue and ivalue['$dnanexus_link'].startswith("file-") or 'primaryFile' in ivalue)

    def compile_input_generic(iname, ivalue):
        if isinstance(ivalue, list):
            return [ compile_input_generic(iname, x) for x in ivalue ]
        elif isinstance(ivalue, dict):
            if is_file(ivalue):
                if 'primaryFile' in ivalue:
                    objid = ivalue['primaryFile']['$dnanexus_link']
                else:
                    objid = ivalue['$dnanexus_link']
                file_info = dxpy.api.file_describe(object_id=objid,
                                                   input_params={'project':dxpy.PROJECT_CONTEXT_ID})
                file_name = file_info['name']
                dxpy.download_dxfile(objid, file_name)
                files = {"path": file_name, "class": "File"}
                if 'secondaryFiles' in ivalue:
                    files.update({'secondaryFiles': compile_input_generic(iname, ivalue['secondaryFiles'])})
                return files
            else:
                return { k : compile_input_generic(k,v) for k,v in ivalue.items() }
        else:
            return ivalue

    print("DNANEXUS INPUTS:\n")
    pprint(dxinputs)
    cwlinputs = { iname : compile_input_generic(iname, ivalue) for iname, ivalue in dxinputs.items() }

    with open("cwlinputs.yml", "w") as f:
        f.write(yaml.safe_dump(cwlinputs))

    print("CWL INPUTS:\n")
    pprint(cwlinputs)

    print("Running CWL tool")
    sh("cwl-runner --default-docker-cmd dx-docker tool.cwl cwlinputs.yml > cwl_job_outputs.json")

    print("Process CWL outputs")
    output = {}
    with open("cwl_job_outputs.json") as f:
        cwloutputs = json.loads(f.read())

    def is_output_file(ovalue):
        return 'class' in ovalue and ovalue['class'] == 'File'

    def compile_output_generic(oname, ovalue):
        if isinstance(ovalue, list):
            return [ compile_output_generic(oname, x) for x in ovalue ]
        elif isinstance(ovalue, dict):
            if is_output_file(ovalue):
                def upload_file(ovalue):
                    return dxpy.dxlink(dxpy.upload_local_file(ovalue['location'][7:], wait_on_close=True))

                files = upload_file(ovalue)
                if 'secondaryFiles' in ovalue:
                    files = {'primaryFile': files, 'secondaryFiles': compile_output_generic(oname, ovalue['secondaryFiles'])}
                return files
            else:
                return { k : compile_output_generic(k,v) for k,v in ovalue.items() }
        else:
            return ovalue

    pprint("CWL OUTPUTS:\n")
    pprint(cwloutputs)

    output = { oname: compile_output_generic(oname, ovalue) for oname, ovalue in cwloutputs.items() }
    for k,v in output.items():
        if not v:
            del output[k]

    pprint("DNANEXUS OUTPUTS:\n")
    pprint(output)


    return output


dxpy.run()
