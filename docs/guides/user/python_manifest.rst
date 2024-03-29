Python Lambda Packager Manifest File
========================================

Usage
*******

To allow for the packager to package several different lambdas at once, we leverage a manifest file. The name of the file is unimportant, but the schema of the file is defined below. The file should be a `.yml`, `.yaml`, or `.json` file.

Spec
######

.. code-block:: yaml

    kind: lambda-packager
    version: # The version of the spec to use. Currently only `1.0.0`.
    lambdas: # List of lambdas to package
      - name: add_to_cell # Build name, only used to keep builds independent. Must be unique
        environment_overrides:
        # Any environment variable supported with the Python Packager documentation

Example
#########

.. code-block:: yaml

    ---
    kind: lambda-packager
    version: 1.0.0 # Manifest file version
    lambdas:
      - name: add_to_cell # This is just used for building, it does not effect the artifact file.
        environment_overrides:
          LAMBDA_CODE_DIR: ./lambdas/mock_processor_objects/add_to_cell
          REQUIREMENTS_FILE: ./requirements.txt
          ARTIFACT_NAME: po_add_to_cell.zip
          FAIL_ON_TOO_BIG: True # Boolean or String is fine.
          SSH_FLIP: True
      - name: extract_cell
        environment_overrides:
          LAMBDA_CODE_DIR: ./lambdas/mock_processor_objects/extract_cell
          REQUIREMENTS_FILE: ./requirements.txt
          ARTIFACT_NAME: po_extract_cell.zip
          FAIL_ON_TOO_BIG: True
          SSH_FLIP: True
      - name: mock_file_writer
        environment_overrides:
          LAMBDA_CODE_DIR: ./lambdas/mock_file_writer
          REQUIREMENTS_FILE: ./requirements.txt
          ARTIFACT_NAME: mock_file_writer.zip
          FAIL_ON_TOO_BIG: True
          SSH_FLIP: True

