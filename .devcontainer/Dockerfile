FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

COPY tools.mk /

RUN su vscode -c "make -f tools.mk tools" \
    && rm tools.mk
