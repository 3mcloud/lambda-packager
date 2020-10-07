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