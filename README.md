# dx-cwl

**Import and run CWL workflows on DNAnexus**

**THIS IS AN ALPHA-PHASE PROJECT.** Please use at your own risk or contact DNAnexus if you are interested.


We have tested this implementation on a few practical workflows of varying complexity and are working towards more complete support of the specification.  More tests, documentation, and improvements to the user experience to come shortly.

The motivation behind `dx-cwl` is to compile a [CWL workflow definition](http://www.commonwl.org/) to a [DNAnexus workflow](https://wiki.dnanexus.com/API-Specification-v1.0.0/Workflows-and-Analyses). This approach enables the user to execute a CWL workflow on DNAnexus and take advantage of the platform's many features including secure execution on multiple regions/clouds.  We use a reference CWL implementation and data structures when possible to adhere maximally to the standard.  CWL types are mapped directly to DNAnexus types when possible and when not, these structures exist as a general JSON data types within the platform.

## Run with DNAnexus CLI

Coming soon.

## Run locally with Docker installation

We have created a Docker repository for `dx-cwl` so you do not have to install all the dependencies to execute it.  Below is an example command of how to use the container.

```
docker run -v $PWD/examples:/examples dnanexus/dx-cwl:alpha compile-workflow /examples/test_bcbio_cwl/somatic/somatic-workflow/main-somatic.cwl --token $MYTOKEN --project cwl
```

This image can run commands exactly like those specified below in "Executing dx-cwl directly".  Please see the [ENCODE example](https://github.com/dnanexus/dx-cwl/blob/master/examples/encode-pipeline.md) for a more detailed walk-through.

## Install code in this repository

### Pre-requisites

* Ensure you have recent version of [dx-toolkit](https://wiki.dnanexus.com/Downloads)
* Install [cwltool](https://github.com/common-workflow-language/cwltool)
* Install [PyYAML](https://pypi.python.org/pypi/PyYAML)
* Clone this repository and run `./get-cwltool.sh` to obtain the appropriate cwltool for DNAnexus applications
* Please create an [API token](https://wiki.dnanexus.com/Command-Line-Client/Login-and-Logout#Authentication-Tokens) and select a project ID that you would like to compile the workflow in

## Executing dx-cwl directly

To compile a workflow, simply point `dx-cwl` to a local workflow on your platform and be sure to provide your authentication token and project name.
The example below is a [test CWL of a bcbio workflow](https://github.com/bcbio/test_bcbio_cwl/).


```
python dx-cwl compile-workflow examples/test_bcbio_cwl/somatic/somatic-workflow/main-somatic.cwl --token $MYTOKEN --project cwl

```

To execute a workflow much like you would with the reference implementation, simply upload the data files and CWL input file onto the platform and run this command on your local installation of `dx-cwl`.

```
python dx-cwl run-workflow main-somatic/main-somatic test_bcbio_cwl/somatic/somatic-workflow/main-somatic-samples.json
```

Here `main-somatic` is the workflow that was compiled to DNAnexus and it is contained in the `main-somatic/` directory on the platform along with other applications and resources required for the workflow. `test_bcbio_cwl/` is literally a copy of the files in that repository on the DNAnexus cloud.

Note that the compiled workflow can be used directly as a typical workflow on DNAnexus as well.

## Related links

* Influenced by [dxWDL](https://github.com/dnanexus-rnd/dxWDL/)
