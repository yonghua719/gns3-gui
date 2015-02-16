# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 GNS3 Technologies Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from unittest.mock import patch, Mock
from gns3.modules.iou.iou_device import IOUDevice
from gns3.ports.port import Port
from gns3.nios.nio_udp import NIOUDP
from gns3.node import Node
from gns3.utils.normalize_filename import normalize_filename


def test_iou_device_init(local_server, project):

    iou_device = IOUDevice(None, local_server, project)


def test_iou_device_setup(iou_device, project):

    with patch('gns3.node.Node.httpPost') as mock:
        iou_device.setup("/tmp/iou.bin", name="PC 1")
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/iou/vms"
        assert kwargs["body"] == {
            "name": "PC 1",
            "path": "/tmp/iou.bin"
        }

        # Callback
        params = {
            "console": 2000,
            "name": "PC1",
            "project_id": "f91bd115-3b5c-402e-b411-e5919723cf4b",
            "vm_id": "aec7a00c-e71c-45a6-8c04-29e40732883c"
        }
        args[1](params)

        assert iou_device.vm_id() == "aec7a00c-e71c-45a6-8c04-29e40732883c"


def test_iou_device_setup_with_uuid(iou_device, project):
    """
    If we have an ID that mean the VM already exits and we should not send startup_script
    """

    with patch('gns3.node.Node.httpPost') as mock:
        iou_device.setup("/tmp/iou.bin", name="PC 1", vm_id="aec7a00c-e71c-45a6-8c04-29e40732883c")
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/iou/vms"
        assert kwargs["body"] == {
            "vm_id": "aec7a00c-e71c-45a6-8c04-29e40732883c",
            "name": "PC 1",
            "path": "/tmp/iou.bin"
        }

        # Callback
        params = {
            "console": 2000,
            "name": "PC1",
            "project_id": "f91bd115-3b5c-402e-b411-e5919723cf4b",
            "vm_id": "aec7a00c-e71c-45a6-8c04-29e40732883c"
        }
        args[1](params)

        assert iou_device.vm_id() == "aec7a00c-e71c-45a6-8c04-29e40732883c"


def test_iou_device_setup_with_initial_config(iou_device, project, tmpdir):
    """
    If we have an ID that mean the VM already exits and we should not send startup_script
    """

    initial_config = str(tmpdir / "config.cfg")
    with open(initial_config, "w+") as f:
        f.write("hostname %h")

    with patch('gns3.node.Node.httpPost') as mock:
        iou_device.setup("/tmp/iou.bin", name="PC 1", vm_id="aec7a00c-e71c-45a6-8c04-29e40732883c", initial_config=initial_config)
        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/iou/vms"
        assert kwargs["body"] == {
            "vm_id": "aec7a00c-e71c-45a6-8c04-29e40732883c",
            "name": "PC 1",
            "path": "/tmp/iou.bin",
            "initial_config": "hostname %h"
        }


def test_update(iou_device):

    new_settings = {
        "name": "Unreal IOU",
    }

    with patch('gns3.node.Node.httpPut') as mock:
        iou_device.update(new_settings)

        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/iou/vms/{vm_id}".format(vm_id=iou_device.vm_id())
        assert kwargs["body"] == new_settings

        # Callback
        args[1]({})


def test_update_initial_config(iou_device, tmpdir):

    initial_config = str(tmpdir / "config.cfg")
    with open(initial_config, "w+") as f:
        f.write("hostname %h")

    new_settings = {
        "name": "Unreal IOU",
        "initial_config": initial_config
    }

    with patch('gns3.node.Node.httpPut') as mock:
        iou_device.update(new_settings)

        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/iou/vms/{vm_id}".format(vm_id=iou_device.vm_id())
        assert kwargs["body"]["name"] == "Unreal IOU"
        assert kwargs["body"]["initial_config"] == "hostname %h"

        # Callback
        args[1]({})