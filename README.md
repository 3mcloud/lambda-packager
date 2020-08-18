# lambda-packager

## **Supported tags and respective `Dockerfile` links**:

- [`python-3.8`](https://github.com/3mcloud/lambda-packager/blob/master/python/3.8/Dockerfile), [`latest`](https://github.com/3mcloud/lambda-packager/blob/master/python/3.8/Dockerfile)
- [`python-3.7`](https://github.com/3mcloud/lambda-packager/blob/master/python/3.7/Dockerfile)
- [`python-3.6`](https://github.com/3mcloud/lambda-packager/blob/master/python/3.6/Dockerfile)
- [`node-12.16`](https://github.com/3mcloud/lambda-packager/blob/master/node/12.16/Dockerfile), [`node-latest`](https://github.com/3mcloud/lambda-packager/blob/master/node/12.16/Dockerfile)


______
## Python

### TL;DR
Lets say all our code is within a `src` directory and within that `src` directory we have a `requirements.txt`. We want the output to be `deployment.zip` at the root of our project. Then all we need to do is:
```bash
	docker run -it --rm \
        -v $(if ${PWD},${PWD},${CURDIR}):/src \ # First mount our code to the container
		3mcloud/lambda-packager:python-3.6
```
And **boom**, `deployment.zip` should be in your repository root.

**Note:** `$(if ${PWD},${PWD},${CURDIR})` is a ternary operator which we use to make it Windows and Mac agnostic with Makefiles.
______
### Container Variables

You can change the default behavior of this packager by using the environment variables of the container

| Variable Name | Default | Required | Description |
|-------------- | ------- | ---------| ----------- |
| `LAMBDA_CODE_DIR` | `./src` | no | Directory, relative to `CI_WORKSPACE` (or absolute), that is to be packaged and zipped. |
| `ARTIFACT_NAME` | `deployment.zip` | no | Path and name of the zip file (or artifact) that will be outputted. Relative to `CI_WORKSPACE` (or absolute). |
| `GLOB_IGNORE` | `*.pyc,__pycache__` | no | Comma delimited glob expressions for files and folder to ignore while zipping. |
| `CI_WORKSPACE` | `$(pwd) - i.e. root level` | no | Workspace directory within the container. |
| `REQUIREMENTS_FILE` | `requirements.txt` | no (python only) | Path relative to `LAMBDA_CODE_DIR` (or absolute) where the requirements file is. If not requirements file is found, it will attempt to use the setup.py |
| `SETUP_FILE` | `setup.py` | no (python only) | Path relative to `LAMBDA_CODE_DIR` (or absolute) where the setup.py file is. |
| `MAX_LAMBDA_SIZE_BYTES` | `50000000` | no (python only) | Used for lambda size checking message. Should be an integer value which represents the maximum size of a lambda in bytes. |
| `FAIL_ON_TOO_BIG` | `False` | no (python only) | If set to `True` the container will exit with a status code of `1` if the lambda is too big. |


________________
## Examples


Our code is in a directory named `code` and we have a `reqs.txt` file within that directory. We want `deployment.zip` to be at the root level of our project.
```bash
	docker run -it --rm \
        -v $(if ${PWD},${PWD},${CURDIR}):/src \ # First mount our project to the container
        -e CI_WORKSPACE=/src \ # We will be working with /src
		-e LAMBDA_CODE_DIR=/code \ # The code to be packaged is within /src/code
		-e REQUIREMENTS_FILE=reqs.txt \ # Requirements are in /src/code/reqs.txt
		3mcloud/lambda-packager:python-3.6
```
Alternatively, lets say we only want to mount the `code` directory and not the entire root of our project:
```bash
	docker run -it --rm \
        -v $(if ${PWD},${PWD},${CURDIR})/code:/src \ # First mount our code to the container
		-e LAMBDA_CODE_DIR=/src \ # The code to be packaged is within /src (Note CI_WORKSPACE is /)
		-e REQUIREMENTS_FILE=reqs.txt \ # Requirements are in /src/reqs.txt
        -e ARTIFACT_NAME=/src/deployment.zip \ # We need to save the zip within /src/ since we didn't mount the root level.
		3mcloud/lambda-packager:python-3.6
```
Lasty, we can try to leverage the default values. Lets say all our code is within a `src` directory and within that `src` directory we have a `requirements.txt`. We want the output to be `deployment.zip` at the root of our project. Then all we need to do is:
```bash
	docker run -it --rm \
        -v $(if ${PWD},${PWD},${CURDIR}):/src \ # First mount our code to the container
		3mcloud/lambda-packager:python-3.6
```
________________
## Node

### TL;DR for Node

Make sure:
- your node code is in a folder called `src`, relative to the working directory
- you have a `package.json` (and preferrably, also a `package-lock.json`) in your working directory

```bash
docker run -it --rm -v $(pwd):/workspace -w /workspace 3mcloud/lambda-packager:node-12.16
```

And **boom**, `deployment.zip` should be in your repository root.

### Container variables for node

You can change the default behavior of this packager by using the environment variables of the container

| Variable Name | Default | Required | Description |
|-------------- | ------- | ---------| ----------- |
| `ARTIFACT_CODE_PREFIX` | Empty | no | name of the directory inside your zip file containing the code |
| `ARTIFACT_NAME` | `deployment.zip` | no | name of your artifact or zip file that you want to output |
| `CONTAINER_BUILD_DIRECTORY` | `/build` | no | build output directory __inside__ your container |
| `CI_WORKSPACE` | Docker working dir | no | workspace directory __inside__ your container |
| `LAMBDA_CODE_DIR` | `src` | no | code directory of your lambda function |


### Examples

See the _Examples_ for Python, except where you see `3mcloud/lambda-packager:python-3.6` replace that 
with `3mcloud/lambda-packager:node-12.16`

The default behavior of the node packager is to assume that the `package.json` and `package-lock.json` 
are in the same directory as the entry point for your application. For example, your application looks like this:

```bash
.
├── app.js
├── package.json
```

Then just use the defaults as shown in the _Examples_.

Some projects, however, have a nested structure. If you have a folder structure that looks like this, which was created by `sam init`:

```bash
.
├── README.md
├── __tests__
│   └── unit
│       └── handlers
│           ├── get-all-items.test.js
│           ├── get-by-id.test.js
│           └── put-item.test.js
├── buildspec.yml
├── env.json
├── events
│   ├── event-get-all-items.json
│   ├── event-get-by-id.json
│   └── event-post-item.json
├── package.json
├── src
│   └── handlers
│       ├── get-all-items.js
│       ├── get-by-id.js
│       └── put-item.js
└── template.yml
```

And you want a package that looks like this on the inside:

```bash
.
├── node_modules
└── src
```

Then use this incantation, from the base folder.

```bash
docker run -it --rm -w /test -v $(pwd):/test \
    -e NPM_PACKAGE_FILE=./package.json \
    -e NPM_PACKAGE_LOCK=./package-lock.json \
    -e LAMBDA_CODE_DIR=src \
    -e ARTIFACT_CODE_PREFIX=src \
    3mcloud/lambda-packager:node-12.16
```