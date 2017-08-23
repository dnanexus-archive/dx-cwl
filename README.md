# dx-cwl: Import and run CWL workflows on DNAnexus

**THIS IS AN ALPHA-PHASE PROJECT. PLEASE USE AT YOUR OWN RISK OR CONTACT DNAnexus IF YOU ARE INTERESTED**
While we have tested this implementation on a few practical workflows of varying complexity, we are working towards more complete support of the specification and enhancing the user experience.  More tests and documentation to come shortly.

The motivation behind `dx-cwl` is to compile a CWL workflow definition to a DNAnexus workflow in a way that is spiritually similar to [dxWDL](https://github.com/dnanexus-rnd/dxWDL/). This allows the user to take advantage of the many features of the platform surrounding workflows and their execution.  This implementation uses a reference CWL implementation and data structures within when possible to adhere maximally to the standard.  CWL types are mapped directly to DNAnexus types when possible and when not, these structures exist as a general JSON data type within the platform.

## Run with DNAnexus CLI

Coming soon.

## Run locally with Docker installation

Coming soon.

## Install code in this repository

### Pre-requisites

* Ensure you have recent version of [dx-toolkit](https://wiki.dnanexus.com/Downloads)
* Install [cwltool](https://github.com/common-workflow-language/cwltool)
* Install [PyYAML](https://pypi.python.org/pypi/PyYAML)
* Clone this repository and run `./get-cwltool.sh` to obtain the appropriate CWLtool for DNAnexus applications
* Please create an [API token](https://wiki.dnanexus.com/UI/API-Tokens) and project that you would like to compile the workflow in

## Executing dx-cwl directly

To compile a workflow, simply point `dx-cwl` to a local workflow on your platform and be sure to provide your authentication token and project name.
The example below [test CWL of a bcbio workflow](https://github.com/bcbio/test_bcbio_cwl/).


```
./dx-cwl compile-workflow examples/test_bcbio_cwl/somatic/somatic-workflow/main-somatic.cwl --token $MYTOKEN --project cwl

```

To execute a workflow much like you would with the reference implementation, simply upload the files onto

```
./dx-cwl run-workflow main-somatic/main-somatic test_bcbio_cwl/somatic/somatic-workflow/main-somatic-samples.json
```

Here `main-somatic` is the workflow that was compiled to DNAnexus and it is contained in the `main-somatic/` directory along with other applications and resources required for the workflow.

Note that the compiled workflow can be used directly as a typical workflow on DNAnexus as well.
