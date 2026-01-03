# gr8pc: A High-Level gRPC Wrapper for python

This library is a direct adaptation of
[py-grpcio](https://github.com/Niche-Solutions-LLC/py-grpcio), featuring a few modifications and
tailored customizations. Depending on your needs, you may find the original repository better suited
to your requirements and preferred practices.

---

## Background and Motivation

As noted before, `gr8pc` is an adaptation of the `py-grpcio` library, with a few key modifications:

- **Python 3.11 Compatibility**: This library is compatible with Python 3.11 (the original library demands >=3.12).
- **Separation between Logic and Protobuf file Generation**: `gr8pc` splits into two subprojects: one for the core server and client logic, and another (optional) CLI tool for `.proto` file generation. This design decision was made to make the dependency on `jinja` not necessary for the core library.
  In other words, the core library won't generate `.proto` files during runtime and will raise an error if it can't find them. The `.proto` file must be generated at development time using the CLI tool.

## Installation

```bash
pip install gr8pc
```

To install the optional CLI:

```bash
pip install gr8gen
```

## Usage

For usage documentation, please refer to the original
[py-grpcio](https://github.com/Niche-Solutions-LLC/py-grpcio) repository.

## Proto Generation Tool

```bash
$ gr8gen --help

usage: gr8gen [-h] [--version] [-o OUT] -s SVCS [SVCS ...]

A CLI tool for processing paths and services.

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -o OUT, --out OUT     Path for output. Must be an existing or new directory. (default: ./proto)
  -s SVCS [SVCS ...], --svcs SVCS [SVCS ...]
                        Python-like import path(s) for service(s). Example: 'path.to.class.Class'. (default: None)
```

The gr8gen tool generates the necessary `.proto` file. Usage:

```bash
gr8gen --output /path/to/proto/folder --service path.to.service.Service path.to.another.service.AnotherService
```

## Acknowledgments

This library is derived directly from the `py-grpcio` package, maintaining much of the original
structure and functionality.