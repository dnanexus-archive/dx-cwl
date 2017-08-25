# Run a basic ENCODE mapping pipeline using dx-cwl

The ENCODE mapping pipeline can be found [here](https://github.com/ENCODE-DCC/pipeline-container/tree/master/local-workflows).

To run it using `dx-cwl` first clone the repository:

```bash
git clone https://github.com/ENCODE-DCC/pipeline-container.git
```

## Compile

Now compile the workflow using the Docker image (see https://get.docker.com/ to quickly install Docker on your system). Please make sure you supply a project ID and [API token](https://wiki.dnanexus.com/Command-Line-Client/Login-and-Logout#Authentication-Tokens).

```bash
docker run --rm -v $PWD/pipeline-container:/pipeline-container dnanexus/dx-cwl:alpha compile-workflow /pipeline-container/local-workflows/encode_mapping_workflow.cwl --token $TOKEN --project $PROJECT
```

The output should look something like this:

```
Selected project project-XXX
Compiling tools/workflows for each step in the workflow
    mapper
    post_processing
    filter_qc
    xcor
    output_folder
Compiling CWL workflow to DNAnexus
Workflow created in /encode_mapping_workflow. ID: workflow-XXX
```

## Run

Although the workflow can be executed like any workflow on the platform, `dx-cwl` also provides a way for you point to files on the platform to run inputs.  For example, if you place the `local-workflows` directory in your project:

```bash
dx cd /
dx upload -r pipeline-container/local-workflows
```

The following command will launch the workflow:

```
docker run --rm dx-cwl:alpha run-workflow encode_mapping_workflow/encode_mapping_workflow local-workflows/encode_mapping_workflow.cwl_test.json --token $TOKEN --project $PROJECT
```

The file `encode_inputs/encode_mapping_workflow.cwl_test.json` contains relative paths to files in the project and these are resolved to unique file identifiers before submitting the workflow for execution.
