<!-- Copyright 2021 Canonical Ltd.
See LICENSE file for licensing details. -->

# Apache Guacd Operator

[![codecov](https://codecov.io/gh/davigar15/charm-apache-guacd/branch/main/graph/badge.svg?token=MA9XWOB018)](https://codecov.io/gh/davigar15/charm-apache-guacd)
[![code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black/tree/main)
[![Run-Tests](https://github.com/davigar15/charm-apache-guacd/actions/workflows/ci.yaml/badge.svg)](https://github.com/davigar15/charm-apache-guacd/actions/workflows/ci.yaml)


[![Apache Guacd](https://charmhub.io/davigar15-apache-guacd/badge.svg)](https://charmhub.io/davigar15-apache-guacd)

## Description

The native server-side proxy used by [Apache Guacamole](https://charmhub.io/davigar15-apache-guacamole).

Guacd is the native server-side proxy used by the Apache Guacamole web application. If you wish to deploy Guacamole, or an application using the Guacamole core APIs, you will need a copy of guacd running.

## Usage

The Apache Guacd Operator may be deployed using the Juju command line as in

```shell
$ juju add-model apache-guacd
$ juju deploy davigar15-apache-guacd --channel edge
```

## OCI Images

- [guacd](https://hub.docker.com/layers/guacamole/guacd/1.3.0/images/sha256-49d43948140f03956124abce4fd8d7e002d61fb19d4c7ca79fcc1638900b0fd1)

## Contributing

Please see the [Juju SDK docs](https://juju.is/docs/sdk) for guidelines
on enhancements to this charm following best practice guidelines, and
`CONTRIBUTING.md` for developer guidance.
