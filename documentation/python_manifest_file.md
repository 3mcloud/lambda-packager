# Python Lambda Packager Manifest File
To allow for the packager to package several different lambdas at once, we leverage a manifest file. The name of the file is unimportant, but the schema of the file is defined below. The file should be a `.yml`, `.yaml`, or `.json` file.
_____
## YAML

### Spec
```yaml
Version: The version of the spec to use. Currently only `1.0.0`.
Lambdas: A list of lambdas to package, where each element in the list is a dictionary of container variables.
```

### Example
```yaml
Version: 1.0.0 # Manifest file version
Lambdas:

  # The following is a list of lambdas to package. Each element in the list can have any of the environment variables specified in the Python Lambda Packager Container Variables EXCEPT `MANIFEST_FILE`.

  - LAMBDA_CODE_DIR: ./lambdas/mock_processor_objects/add_to_cell
    REQUIREMENTS_FILE: ./requirements.txt
    ARTIFACT_NAME: po_add_to_cell.zip
    FAIL_ON_TOO_BIG: True # Boolean or String is fine.
    SSH_FLIP: True

  - LAMBDA_CODE_DIR: ./lambdas/mock_processor_objects/extract_cell
    REQUIREMENTS_FILE: ./requirements.txt
    ARTIFACT_NAME: po_extract_cell.zip
    FAIL_ON_TOO_BIG: True
    SSH_FLIP: True

  - LAMBDA_CODE_DIR: ./lambdas/mock_file_writer
    REQUIREMENTS_FILE: ./requirements.txt
    ARTIFACT_NAME: mock_file_writer.zip
    FAIL_ON_TOO_BIG: True
    SSH_FLIP: True

```
