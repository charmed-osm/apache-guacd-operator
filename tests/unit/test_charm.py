# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.

import pytest
from ops.model import ActiveStatus, BlockedStatus, MaintenanceStatus
from ops.testing import Harness
from pytest_mock import MockerFixture

from charm import ApacheGuacdCharm


@pytest.fixture
def harness(mocker: MockerFixture):
    mocker.patch(
        "charm.ApacheGuacdCharm.pod_ip",
        new_callable=mocker.PropertyMock,
    )
    guacd_harness = Harness(ApacheGuacdCharm)
    guacd_harness.begin()
    yield guacd_harness
    guacd_harness.cleanup()


def test_guacd_pebble_ready(mocker: MockerFixture, harness: Harness):
    spy = mocker.spy(harness.charm, "_restart")
    harness.charm.on.guacd_pebble_ready.emit("guacd")
    assert harness.charm.unit.status == ActiveStatus()
    assert spy.call_count == 1


def test_config_changed_can_connect(mocker: MockerFixture, harness: Harness):
    spy = mocker.spy(harness.charm, "_restart")
    harness.charm.on.config_changed.emit()
    assert harness.charm.unit.status == ActiveStatus()
    assert spy.call_count == 1


def test_config_changed_cannot_connect(mocker: MockerFixture, harness: Harness):
    spy = mocker.spy(harness.charm, "_restart")
    container_mock = mocker.Mock()
    container_mock.can_connect.return_value = False
    mocker.patch(
        "charm.ApacheGuacdCharm.container",
        return_value=container_mock,
        new_callable=mocker.PropertyMock,
    )
    harness.charm.on.config_changed.emit()
    assert harness.charm.unit.status == MaintenanceStatus("waiting for pebble to start")
    assert spy.call_count == 0


def test_restart_service_service_not_exists(mocker: MockerFixture, harness: Harness):
    container_mock = mocker.Mock()
    mocker.patch(
        "charm.ApacheGuacdCharm.container",
        return_value=container_mock,
        new_callable=mocker.PropertyMock,
    )
    mocker.patch(
        "charm.ApacheGuacdCharm.services", return_value={}, new_callable=mocker.PropertyMock
    )
    harness.charm._restart_service()
    container_mock.restart.assert_not_called()


def test_charm_error(mocker: MockerFixture, harness: Harness):
    mocker.patch(
        "charm.ApacheGuacdCharm.pod_ip",
        return_value=None,
        new_callable=mocker.PropertyMock,
    )
    harness.charm._restart()
    assert harness.charm.unit.status == BlockedStatus("missing unit ip")
