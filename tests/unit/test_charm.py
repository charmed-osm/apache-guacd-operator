# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.

import pytest
from ops.model import ActiveStatus, MaintenanceStatus
from ops.testing import Harness
from pytest_mock import MockerFixture

from charm import ApacheGuacdCharm

guacd_pod_ip_mock = None


@pytest.fixture
def harness(mocker: MockerFixture):
    global guacd_pod_ip_mock
    guacd_pod_ip_mock = mocker.patch("charm.guacd.pod_ip")
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


def test_relation_non_leader(mocker: MockerFixture, harness: Harness):
    rel_id = harness.add_relation("guacd", "test-charm")
    harness.add_relation_unit(rel_id, "test-charm/1")
    harness.charm.on.start.emit()
    relation = harness.charm.model.get_relation("guacd", rel_id)
    assert "hostname" not in relation.data[harness.charm.app]
    assert "port" not in relation.data[harness.charm.app]
    assert "hostname" in relation.data[harness.charm.unit]
    assert "port" in relation.data[harness.charm.unit]


def test_relation_leader(mocker: MockerFixture, harness: Harness):
    harness.set_leader(True)
    rel_id = harness.add_relation("guacd", "test-charm")
    harness.add_relation_unit(rel_id, "test-charm/1")
    harness.charm.on.start.emit()
    relation = harness.charm.model.get_relation("guacd", rel_id)
    assert "hostname" in relation.data[harness.charm.app]
    assert "port" in relation.data[harness.charm.app]
    assert "hostname" in relation.data[harness.charm.unit]
    assert "port" in relation.data[harness.charm.unit]
