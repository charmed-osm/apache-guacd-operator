#!/usr/bin/env python3
# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.

"""Apache Guacd charm module."""

import logging

from charms.davigar15_apache_guacd.v0 import guacd
from ops.charm import CharmBase, ConfigChangedEvent, WorkloadEvent
from ops.framework import StoredState
from ops.main import main
from ops.model import ActiveStatus, MaintenanceStatus

logger = logging.getLogger(__name__)

REQUIRED_CONFIG = ()


class ApacheGuacdCharm(CharmBase):
    """Apache Guacd Charm operator."""

    _stored = StoredState()

    def __init__(self, *args):
        super().__init__(*args)
        event_observe_mapping = {
            self.on.guacd_pebble_ready: self._on_guacd_pebble_ready,
            self.on.config_changed: self._on_config_changed,
        }
        for event, observer in event_observe_mapping.items():
            self.framework.observe(event, observer)
        self.guacd = guacd.GuacdProvides(self)

    @property
    def container(self):
        """Property to get guacd container."""
        return self.unit.get_container("guacd")

    @property
    def services(self):
        """Property to get the services in the container plan."""
        return self.container.get_plan().services

    def _on_guacd_pebble_ready(self, _: WorkloadEvent):
        self._restart()

    def _on_config_changed(self, event: ConfigChangedEvent):
        if self.container.can_connect():
            self._restart()
        else:
            logger.info("pebble socket not available, deferring config-changed")
            event.defer()
            self.unit.status = MaintenanceStatus("waiting for pebble to start")

    def _restart(self):
        layer = self._get_pebble_layer()
        self._set_pebble_layer(layer)
        self._restart_service()
        self.unit.status = ActiveStatus()

    def _restart_service(self):
        container = self.container
        if "guacd" in self.services:
            container.restart("guacd")
            logger.info("guacd service has been restarted")

    def _get_pebble_layer(self):
        return {
            "summary": "guacd layer",
            "description": "pebble config layer for guacd",
            "services": {
                "guacd": {
                    "override": "replace",
                    "summary": "guacd service",
                    "command": f"/usr/local/guacamole/sbin/guacd -b {guacd.pod_ip()} -L info -f",
                    "startup": "enabled",
                    "environment": {
                        "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                        "LC_ALL": "C.UTF-8",
                        "LD_LIBRARY_PATH": "/usr/local/guacamole/lib",
                    },
                }
            },
        }

    def _set_pebble_layer(self, layer):
        self.container.add_layer("guacad", layer, combine=True)


if __name__ == "__main__":  # pragma: no cover
    main(ApacheGuacdCharm, use_juju_for_storage=True)
