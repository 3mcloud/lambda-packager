# lambda-packager
Package code for Python AWS Lambda functions using a docker container.


### TL;DR for Python3.6

Make sure:
- your python code is in a folder called `./src`
- you have a `requirements.txt` in that `src` folder

```
docker run -it --rm -v $(pwd):$(pwd) -w $(pwd) 3mcloud/lambda-packager:python-3.6
```

And **boom**, `deployment.zip` should be in your repository root.

##### Container Variables

You can change the default behavior of this packager by using the environment variables of the container

| Variable Name | Default | Required | Description |
|-------------- | ------- | ---------| ----------- |
| `LAMBDA_CODE_DIR` | `src` | no | code directory of your lambda function |
| `ARTIFACT_NAME` | `deployment.zip` | no | name of your artifact or zip file that you want to output |
| `CI_WORKSPACE` | `$(pwd)` | no | workspace directory __inside__ your container |
| `REQUIREMENTS_FILE` | `requirements.txt` | no (python only) | Your pip requirements file |

### Build this container

If we don't have this available as a docker container in 3mcloud, build it by using the following command:

```
docker build -t 3mcloud/lambda-packager:python-3.6 python/3.6/.
```


### Examples

Change your source directory to `codez`:

```
docker run -it --rm -e LAMBDA_CODE_DIR=codez -v $(pwd):$(pwd) -w $(pwd) 3mcloud/lambda-packager:python-3.6
```

Change artifact output zip file name:
```
docker run -it --rm -e ARTIFACT_NAME=boston.zip -v $(pwd):$(pwd) -w $(pwd) 3mcloud/lambda-packager:python-3.6
```

Do some crazy explicit stuff with the volume mapping:

```
docker run -it --rm -v /Users/johndoe/my-lambda-source:/custom_build_dir -w /Users/johndoe/my-lambda-source 3mcloud/lambda-packager:python-3.6
```
