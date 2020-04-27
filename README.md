# docker-make

docker-make is a simple command line tool for developer teams to unify their build and delivery process of Docker images. It is easy to include into build pipelines and helps establishing best practices on Dockerfiles.

The main features of docker-make are:

- Dockerfile linting
- Execution of docker build and push commands introducing useful, consistent CI tags and labels
- Regulation of image pushes

## Installation

docker-make is published as a fully self-contained binary on the [release page](https://github.com/fi-ts/docker-make/releases).

## Getting Started

1.  Place a file `docker-make.yaml` into your build project, the same location in which you store your `Dockerfile`. You can start with the following template:
   
    ```yaml
    ---
    version: '1'
    # the name of the docker image to be built
    name: your-application
    # the namespace in which the built image will be stored
    username: your-project
    # the registry host to push containers to
    registry-host: your.registry.com
    builds:
      -
        name: Latest Stable
        tags:
          - latest
    ```
    
    For a more complete example, refer to the [reference](#docker-make-yaml-reference).

1.  Lint your `Dockerfile` to check for improvements.

    ```bash
    # in your project directory
    docker-make --only-lint
    ```

1.  Consider a dry run if you only want to see the commands which docker-make would run on your machine.

    ```bash
    docker-make --dry-run
    ```

1.  If you are fine with what you see, build!

    ```bash
    docker-make --summary
    ```

## Configuration

You can list the options of docker-make with `docker-make -h`. 

The usage will also show how to configure docker-make with config files or environment variables.

## docker-make.yaml Reference

You can find a complete reference of a docker-make.yaml (version 1) [here](test/mock/docker-make.yaml).

## Regulate who can push container images

With the options `--push-only-to-defined-registries` and `--push-only-to-specific-git-projects`, you can configure docker-make to "soft regulate" image pushes in CI. 

The `/etc/docker-make/registries.yaml` defines an inventory of your registries and repository remote urls that are allowed to push to them. It can look like this:

```yaml
---
registries:
  registry.a.com:
    repositories:
      - "github.com/fi-ts/docker-make"
```

Repositories are derived from Git remote URL of the current working directory that you are running docker-make from.

For stronger regulation, you need to introduce registry authentication. You can configure docker-make to use registry authentication and store registry credentials in the same file, if you want:

```yaml
---
registries:
  registry.a.com:
    repositories:
      - "registry.a.com/domain-a"
    auth:
      user: some-user
      password: some-password
```

However, it is actually best practice not to store the password as plaintext in a file. For this reason, you can also set the environment variables `DOCKER_MAKE_REGISTRY_LOGIN_USER` and `DOCKER_MAKE_REGISTRY_LOGIN_PASSWORD`, which you can inject into your CI build.

# Development

## Testing

To run the tests of this project, you may want to install nose and coverage:

```
pip install -e .[dev]
```

After the installation, you can run the tests from the project root like so:

```
nosetests
```
