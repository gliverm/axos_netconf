# ------------------------------
# Multistage Docker File
# ------------------------------
# ------------------------------
# IMAGE: Target 'base' image
# docker build --file Dockerfile --target base -t st-scale-toolbox-base:test .
# docker run -it --rm --name base st-scale-toolbox-base:test
# ------------------------------
ARG UBUNTU_RELEASE=24.04
FROM ubuntu:${UBUNTU_RELEASE} AS base
LABEL maintainer="Gayle Livermore <gayle.livermore@calix.com>"
ENV LANG="C.UTF-8"
ENV LC_ALL="C.UTF-8"
ENV LC_CTYPE="C.UTF-8"
ENV TZ=America/Chicago
ENV SHELL /bin/bash
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
# hadolint ignore=DL3008
RUN echo "===> Adding build dependencies..."  && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install --no-install-recommends --yes \
    git \
    libfontconfig1 \
    ca-certificates \
    wget \
    curl && \
    apt-get autoremove && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
# Basic install of git check
RUN ["git", "--version"]

# ------------------------------
# IMAGE: Target 'pythonbase' for base of all images that need Python
# docker build --file Dockerfile --target pythonbase -t st-scale-toolbox-pythonbase:test .
# docker build --no-cache --file Dockerfile --target pythonbase -t st-scale-toolbox-pythonbase .
# docker run -it --rm --name st-scale-toolbox pythonbase st-scale-toolbox-pythonbase:test
# ------------------------------
FROM base AS pythonbase
# hadolint ignore=DL3008
RUN echo "===> Adding build dependencies..."  && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install --no-install-recommends --yes \
    python3 \
    build-essential \
    openssh-client \
    python3-dev \
    python3-pip \
    python3-pycurl && \
    apt-get autoremove && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED=1
# It is a good idea to upgrade package management tools to latest
# hadolint ignore=DL3013
RUN echo "===> Installing pip ..." && \
    python3 -m pip config set global.break-system-packages true && \
    python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir --upgrade setuptools && \
    python3 -m pip install --no-cache-dir --ignore-installed --upgrade wheel && \
    python3 -m pip install --no-cache-dir --upgrade pyinstaller && \
    python3 -m pip install --no-cache-dir --upgrade pipenv && \
    python3 -m pip list

# ------------------------------
# IMAGE: Target 'dev' for code development - no Python pkgs loaded
# docker build --file Dockerfile --target dev -t st-scale-toolbox-dev:test .
# docker run -it --rm --name st-scale-toolbox-dev st-scale-toolbox-dev:test
# docker container run -it -d -v st-scale-toolbox:/development -v ~/.ssh:/root/ssh -v ~/.gitconfig:/root/.gitconfig --name st-scale-toolbox-dev st-scale-toolbox-dev:test
# docker container run -it -v st-scale-toolbox:/development -v ~/.ssh:/root/ssh -v ~/.gitconfig:/root/.gitconfig --name st-scale-toolbox-dev st-scale-toolbox-dev:test
# ------------------------------
FROM pythonbase AS dev
ARG PROJECT_DIR=/development
RUN echo "===> creating working directory..."  && \
    mkdir -p $PROJECT_DIR
WORKDIR $PROJECT_DIR

# ------------------------------
# IMAGE: Target 'qa' for static code analysis and unit testing
# Future: Consider benefit lint shell script in addition to below
# Install the latest static code analysis tools
# docker build --file Dockerfile --target qa -t st-scale-toolbox-qa:test .
# docker run -i --rm -v ${PWD}:/code st-scale-toolbox-qa:test pylint --exit-zero --rcfile=setup.cfg **/*.py
# docker run -i --rm -v ${PWD}:/code st-scale-toolbox-qa:test flake8 --exit-zero
# docker run -i --rm -v ${PWD}:/code st-scale-toolbox-qa:test bandit -r --ini setup.cfg
# docker run -i --rm -v $(pwd):/code -w /code st-scale-toolbox-qa:test black --check --exclude st-scale-toolbox/tests/ st-scale-toolbox/ || true
# docker run -i --rm -v ${PWD}:/code st-scale-toolbox-unittest:test pytest --with-xunit --xunit-file=pyunit.xml --cover-xml --cover-xml-file=cov.xml st-scale-toolbox/tests/*.py
# ------------------------------
FROM pythonbase AS qa
WORKDIR /
COPY Pipfile .
COPY Pipfile.lock .
# Ensure linting tools are latest 
# hadolint ignore=DL3013
RUN pipenv install --dev --deploy --system && \
    pip install --upgrade --no-cache-dir pylint flake8 bandit black
WORKDIR /code/

# ------------------------------
# IMAGE: Target 'builder' builds production app utilizing pipenv
# docker build --file Dockerfile --target builder -t st-scale-toolbox:builder .
# docker run -it --rm --name builder st-scale-toolbox:builder sh
# ------------------------------
FROM pythonbase as builder
RUN echo "===> Installing specific python package versions ..."
WORKDIR /
COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv install --system --deploy
COPY ./app /app
RUN echo "===> Building toolbox application runtime . . ." && \
    pyinstaller \
        --onefile \
        app/toolbox.py && \
    ls && \
    ls dist/toolbox

# ------------------------------
# IMAGE: Target 'app' for final production app build
# docker build --file Dockerfile --target app -t st-scale-toolbox:app .
# docker run -it --rm --name st-scale-toolbox st-scale-toolbox:app sh
# docker run -it --rm -v $PWD/config:/config --name st-scale-toolbox st-scale-toolbox:app bash
# docker run -it --rm -v $PWD/home/toolboxuser/config:/config --name st-scale-toolbox st-scale-toolbox:app bash
# docker run -it --rm -v $PWD/config:/toolbox/config --name st-scale-toolbox st-scale-toolbox:app bash
# Using volumnes with a username different than host is problematic: https://github.com/moby/moby/issues/2259
# ------------------------------
FROM base as app
WORKDIR /
RUN echo "===> Install toolbox ..."
COPY --from=builder /dist/toolbox /opt/toolbox
ENV PATH "$PATH:/opt"
WORKDIR /toolbox
# Note: /config : Location of app configuration files
RUN echo "===> Setting working directories..." && \
    mkdir /toolbox/config && \
    mkdir /toolbox/project
VOLUME /toolbox/config
VOLUME /toolbox/project
RUN ["toolbox", "--help"]
CMD ["toolbox", "--help"]