
## Prerequisites

- Python 3.9.4
- ElasticSearch cluster
- Huggingface hub


### Python Environment Setup
-----
For setting up the environment, first we install `pyenv` and then initiate either local or global python versions for the env setups. For MacOS you can use `homebrew` for installation but it's recommended to use `pyenv installer` as follows:

```bash
$brew install openssl readline sqlite3 xz zlib
$curl https://pyenv.run | bash
```

once the installation is completed, add the following items to your `.bash_profile` or `.zshrc` and source it or just run the command line:

```bash
$export PYENV_ROOT="$HOME/.pyenv"
$export PATH="$HOME/.pyenv/bin:$PATH"
$eval "$(pyenv init -)"
$eval "$(pyenv virtualenv-init -)"
```

Once the `pyenv` is setup, install the required  versions of python and assign the local python as follows:

```bash
$pyenv install 3.9.4
$pyenv local 3.9.4
```

Next step to set up the environment is using [Poetry](https://python-poetry.org/docs/). Poetry is a python package management system. For MacOS, use the following for installation:

```bash
$curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

If you notice poetry gets installed in `$HOME/.poetry` and it automatically writes the `export PATH="$HOME/.poetry/bin:$PATH"` in `.bash_profile` or `.zshrc`. If you want to have the `PATH` unchanged make sure to remove this line or use `--no-modify-path` during installation. To ensure the installation you can check `poetry --version`.

Once poetry is ready you can make a virtualenv and install the package dependencies as follows:

```bash
$pyenv local 3.9.4
$poetry env use 3.9.4
$poetry shell
$poetry install
$pre-commit install
```

First you activate the local python version at the root of your project, then make an env using that python version then activate the virtualenv and after that install the `.lock` file if it exists or `poetry add` if you are building the project from scratch. Maker sure to mark the dev dependencies as `add -D`.

Note, make sure to install the `pre-commit` to enforce the hooks prior commiting your new codes. Othrerwise, the code will not be checked for the agreed upong code styles.


### Elasticsearch Cluster Setup
----
There are different ways of setting up the Elasticsearch cluster. This [link](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html) provides a thorough explanations of the required steps. If you are also interested to install Kibana, a visualization tool, alongside the elasticsearch stack you can follow this [link](https://www.elastic.co/guide/en/kibana/8.8/docker.html) that provides information about installing Kibana.
All the steps for setting up elasticsearch and kibana stack have also been provided as a docker installation file, `docker-compose.yml` in our project root. This yaml file contains all the cert steps and setups for a single node cluster. To get our cluster up and running we do the following items:
1. Create a `.env` file with the following information in it


        # Password for the 'elastic' user (at least 6 characters)
        ELASTIC_PASSWORD=
        ELASTIC_USER=elastic

        # Password for the 'kibana_system' user (at least 6 characters)
        KIBANA_PASSWORD=

        # Version of Elastic products
        STACK_VERSION=8.8.1

        # Set the cluster name
        CLUSTER_NAME=es-kibana-cluster

        # Set to 'basic' or 'trial' to automatically start the 30-day trial
        LICENSE=basic
        #LICENSE=trial

        # Port to expose Elasticsearch HTTP API to the host
        ES_PORT=9200
        #ES_PORT=127.0.0.1:9200

        # Port to expose Kibana to the host
        KIBANA_PORT=5601

        # Increase or decrease based on the available host memory (in bytes)
        MEM_LIMIT=1073741824


2. Run docker-compose command

        docker-compose up -d


3. Get a copy of cert in somewhere local to use for the ES clients access

        docker cp elastic_semantic_search_es01_1:/usr/share/elasticsearch/config/certs/ca/ca.crt ~/.creds


Going forward, we can use the `~/.creds/ca.crt` as our cert file in our elasticsearch client side.


### Commit Messages
----
For this project, we use the following format: `type: message`.

* for example: `feat: added a feature view for the Iris dataset.`

You can refer to this [cheatsheet](https://gist.github.com/joshbuchea/6f47e86d2510bce28f8e7f42ae84c716) on writing semantic commit messages.

### Changelog
----
Please follow the patterns outlined in [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) when making changes to `CHANGELOG.md`.
* Put yourself in the user's shoes and think about what they would want to see in the log.

### Versioning
------
Follow the semantic versioning standards which are outlined in this [guide](https://semver.org/).
* **Do not** include `v` or `V` in the release version (e.g. `v1.0.0`).
