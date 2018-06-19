import os
import dxpy
import json
import yaml
import subprocess
from pprint import pprint

CWLTOOL_VERSION = "1.0.20171017195544"

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
    sh("apt-get update")
    sh("apt-get install python-virtualenv samtools")
    sh("git clone --recursive https://github.com/dnanexus/dx-toolkit.git")
    sh("cd dx-toolkit && git checkout 0c818a5cce7164119e7a89d7415770e1ff2caece && cd ..")
    sh("make -C dx-toolkit python dx-docker")
    os.environ["PATH"] = "/home/dnanexus/dx-toolkit/bin"+":"+os.environ["PATH"]
    os.environ["PYTHONPATH"] = "/home/dnanexus/dx-toolkit/share/dnanexus/lib/python2.7/site-packages:/home/dnanexus/dx-toolkit/lib64/python2.7/site-packages"+":"+os.environ["PYTHONPATH"]

    print "Installing cwltool"
    sh("pip install -U pip wheel setuptools")
    sh("pip install cwltool=={}".format(CWLTOOL_VERSION))
    sh("curl https://nodejs.org/dist/v6.11.2/node-v6.11.2-linux-x64.tar.gz | tar xzvf - --strip-components 1 -C /usr/local/ > /dev/null")

    folder = open("output_folder.txt").read()

    print("Download inputs and create CWL file")
    with open("job_input.json") as f:
        dxinputs = json.loads(f.read())

    # TODO: get rid of this small section as it is outmoded
    tool = yaml.load(open("tool.cwl").read())
    if isinstance(tool['inputs'], list):
        tool['inputs'] = {i['id']:i for i in tool['inputs']}
    if isinstance(tool['outputs'], list):
        tool['outputs'] = {i['id']:i for i in tool['outputs']}
    pprint(tool)

    skip_downloads = False
    if 'hints' in tool:
        for h in tool['hints']:
            if 'class' in h and h['class'] == 'dx:InputResourceRequirement' and h['indirMin'] == 0:
                print("Skipping downloads as this is a book-keeping task")
                skip_downloads = True
                break


    def is_file(ivalue):
        return isinstance(ivalue, dict) and ('$dnanexus_link' in ivalue and ivalue['$dnanexus_link'].startswith("file-") or 'primaryFile' in ivalue)

    def is_directory(ivalue):
        return isinstance(ivalue, dict) and 'class' in ivalue and ivalue['class'] == 'Directory'

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
                sh("mkdir -p {}".format(objid))
                file_name = os.path.join(objid, file_info['name'])
                if skip_downloads:
                    sh("echo {} > {}".format(objid, file_name))
                else:
                    dxpy.download_dxfile(objid, file_name)
                files = {"path": file_name, "class": "File"}
                if 'secondaryFiles' in ivalue:
                    files.update({'secondaryFiles': compile_input_generic(iname, ivalue['secondaryFiles'])})
                return files
            elif is_directory(ivalue):
                basedir_loc = os.path.dirname(ivalue['location'])
                sh("mkdir -p {}".format(basedir_loc))
                sh("unset DX_WORKSPACE_ID && dx cd $DX_PROJECT_CONTEXT_ID: && cd {} && dx download -rf {}".format(basedir_loc, ivalue['location']))
                return ivalue
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
    sh("mkdir -p cwloutputs")
    sh("cwltool --outdir cwloutputs --user-space-docker-cmd dx-docker tool.cwl cwlinputs.yml > cwl_job_outputs.json")

    print("Process CWL outputs")
    output = {}
    with open("cwl_job_outputs.json") as f:
        cwloutputs = json.loads(f.read())

    def is_output_file(ovalue):
        return 'class' in ovalue and ovalue['class'] == 'File'

    def is_output_directory(ovalue):
        return 'class' in ovalue and ovalue['class'] == 'Directory'

    def compile_output_generic(oname, ovalue):
        if isinstance(ovalue, list):
            return [ compile_output_generic(oname, x) for x in ovalue ]
        elif isinstance(ovalue, dict):
            if is_output_file(ovalue):
                def upload_file(ovalue):
                    sh("unset DX_WORKSPACE_ID && dx cd $DX_PROJECT_CONTEXT_ID: && dx mkdir -p {}".format(folder))
                    return dxpy.dxlink(dxpy.upload_local_file(ovalue['location'][7:], wait_on_close=True, project=dxpy.PROJECT_CONTEXT_ID, folder=folder))

                if skip_downloads:
                    files = dxpy.dxlink(open(ovalue['location'][7:]).read().rstrip())
                else:
                    files = upload_file(ovalue)
                if 'secondaryFiles' in ovalue:
                    files = {'primaryFile': files, 'secondaryFiles': compile_output_generic(oname, ovalue['secondaryFiles'])}
                return files

            # TODO: This feature needs to be completed to reset env here, smartly check whether files exist already, and work for inputs
            elif is_output_directory(ovalue):
                sh("unset DX_WORKSPACE_ID && dx cd $DX_PROJECT_CONTEXT_ID: && dx upload -r {}".format(ovalue['path']))
                return ovalue
            else:
                return { k : compile_output_generic(k,v) for k,v in ovalue.items() }
        else:
            return ovalue

    pprint("CWL OUTPUTS:\n")
    pprint(cwloutputs)

    output = { oname: compile_output_generic(oname, ovalue) for oname, ovalue in cwloutputs.items() }

    # Ensure that an optional output (CWL 'null' == JSON None) isn't included in DNAnexus output
    for k,v in output.items():
        if not v:
            del output[k]

    pprint("DNANEXUS OUTPUTS:\n")
    pprint(output)


    return output

dxpy.run()
