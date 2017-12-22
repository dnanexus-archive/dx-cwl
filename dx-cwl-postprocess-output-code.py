import os
import dxpy
import json
import yaml
import subprocess
from pprint import pprint

# TODO: potentially pull these out to common utilities
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
    folder = open("output_folder.txt").read()
    with open("job_input.json") as f:
        dxinputs = json.loads(f.read())

    def is_file(ivalue):
        return isinstance(ivalue, dict) and ('$dnanexus_link' in ivalue and ivalue['$dnanexus_link'].startswith("file-") or 'primaryFile' in ivalue)

    def is_directory(ivalue):
        return isinstance(ivalue, dict) and 'class' in ivalue and ivalue['class'] == 'Directory'

    def compile_input_generic(iname, ivalue):
        if isinstance(ivalue, list):
            for x in ivalue:
                compile_input_generic(iname, x)
        elif isinstance(ivalue, dict):
            if is_file(ivalue):
                if 'primaryFile' in ivalue:
                    objid = ivalue['primaryFile']['$dnanexus_link']
                else:
                    objid = ivalue['$dnanexus_link']
                sh("unset DX_WORKSPACE_ID && dx mv $DX_PROJECT_CONTEXT_ID:{} $DX_PROJECT_CONTEXT_ID:{}".format(objid, folder))
                if 'secondaryFiles' in ivalue:
                    compile_input_generic(iname, ivalue['secondaryFiles'])
            elif is_directory(ivalue):
                pass
                #basedir_loc = os.path.dirname(ivalue['location'])
                #sh("unset DX_WORKSPACE_ID && dx mv $DX_PROJECT_CONTEXT_ID:{} $DX_PROJECT_CONTEXT_ID:{}".format(ivalue['location'], folder))
            else:
                for k,v in ivalue.items():
                    compile_input_generic(k,v)
        else:
            return ivalue

    print("DNANEXUS INPUTS:\n")
    pprint(dxinputs)
    for iname, ivalue in dxinputs.items():
        compile_input_generic(iname, ivalue)


    return dxinputs


dxpy.run()
