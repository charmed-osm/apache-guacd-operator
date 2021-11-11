# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.

from ipaddress import IPv4Address

import pytest
from charms.davigar15_apache_guacd.v0.guacd import GuacdRequires, pod_ip
from pytest_mock import MockerFixture


@pytest.fixture
def requires(mocker: MockerFixture):
    charm = mocker.Mock()
    relation_events = mocker.Mock()
    charm.on = {"guacd": relation_events}
    stored = mocker.Mock()
    requires = GuacdRequires(charm, stored)
    stored.set_default.assert_called_once_with(guacd_hostname=None, guacd_port=None)
    requires.charm.on = mocker.Mock()
    return requires


def test_requires(mocker: MockerFixture, requires: GuacdRequires):
    # Emit relation-changed event with relation data emtpy
    relation_changed_event_mock = mocker.Mock()
    relation_changed_event_mock.relation.data = {}
    requires._on_relation_changed(relation_changed_event_mock)
    requires.charm.on.guacd_changed.emit.not_called()
    # Emit relation-changed event with relation data (first time)
    relation_changed_event_mock.app = "app"
    relation_changed_event_mock.relation.data = {"app": {"hostname": "1.1.1.1", "port": "4822"}}
    requires._on_relation_changed(relation_changed_event_mock)
    assert requires.charm.on.guacd_changed.emit.call_count == 1
    assert requires.hostname == "1.1.1.1"
    assert requires.port == "4822"
    # Emit relation-changed event with relation data (second time)
    # In the second time, since the data of the relation has not changed,
    # the amount of call_counts in the guacd_change event emitter should remain the same
    requires._on_relation_changed(relation_changed_event_mock)
    assert requires.charm.on.guacd_changed.emit.call_count == 1
    # Emit relation-changed event with changed in relation data
    # This time, the guacd_changed event must have been emitted.
    relation_changed_event_mock.relation.data = {"app": {"hostname": "2.2.2.2", "port": "4822"}}
    requires._on_relation_changed(relation_changed_event_mock)
    assert requires.charm.on.guacd_changed.emit.call_count == 2


def test_pod_ip(mocker: MockerFixture):
    socket_mock = mocker.patch("charms.davigar15_apache_guacd.v0.guacd.socket")
    socket_mock.getfqdn.return_value = "host"
    socket_mock.gethostbyname.return_value = "1.1.1.1"
    assert pod_ip() == IPv4Address("1.1.1.1")
    assert socket_mock.getfqdn.call_count == 1
    socket_mock.gethostbyname.assert_called_once_with("host")
