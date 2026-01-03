#   Hyrrokkin - a library for building and running executable graphs
#
#   MIT License - Copyright (C) 2022-2025  Visual Topology Ltd
#
#   Permission is hereby granted, free of charge, to any person obtaining a copy of this software
#   and associated documentation files (the "Software"), to deal in the Software without
#   restriction, including without limitation the rights to use, copy, modify, merge, publish,
#   distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
#   Software is furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in all copies or
#   substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
#   BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#   NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#   DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import io
from typing import Callable
import uuid
from threading import Event

from hyrrokkin.interfaces.topology_listener_api import TopologyListenerAPI
from hyrrokkin_engine.message_utils import MessageUtils
from hyrrokkin.interfaces.topology_api import TopologyApi
from hyrrokkin.interfaces.schema_api import NodeTypeApi, LinkTypeApi, SchemaTypeApi
from hyrrokkin.interfaces.client_api import ClientApi

from hyrrokkin.utils.type_hints import JsonType


class TopologyServiceClient(TopologyApi):

    def __init__(self, send_fn):
        self.send_fn = send_fn
        self.pending_reference = None
        self.pending_reference_event = Event()
        self.pending_reference_message = None
        self.listeners = []

    def send(self, *comps):
        self.send_fn(MessageUtils.encode_message(*comps))

    def recv(self, msg_bytes):
        msg = MessageUtils.decode_message(msg_bytes)
        self.handle(*msg)

    def handle(self, *msg):
        header = msg[0]
        if "ref" in header and header["ref"] == self.pending_reference:
            self.pending_reference_message = msg
            self.pending_reference_event.set()

    def add_node(self, node_id: str | None, node_type_id: str, metadata: dict[str, JsonType] = {},
                 properties: dict[str, JsonType] = {},
                 data: dict[str, bytes] = {}, copy_from_node_id: str = "", ref: str | None = None) -> str:

        data_keys = []
        data_values = []
        for key, value in data.items():
            data_keys.append(key)
            data_values.append(value)

        self.pending_reference = ref or self.__create_reference()
        self.send({
            "ref": self.pending_reference,
            "action": "request_add_node",
            "node_id": node_id,
            "node_type": node_type_id,
            "metadata": metadata,
            "properties": properties,
            "data_keys": data_keys,
            "copy_from_node_id": copy_from_node_id
        }, *data_values)

        self.pending_reference_event.wait()
        self.pending_reference_event.clear()
        return self.pending_reference_message[0]["node_id"]

    def run_task(self, task_name: str, input_port_values: dict[str, bytes | list[bytes]], output_ports: list[str],
                 ref: str | None = None) -> dict[str, bytes]:

        input_ports = {}
        input_values = []

        ref = self.__create_reference()

        for (input_port, value) in input_port_values.items():
            if isinstance(value, list):
                input_ports[input_port] = {"start_index": len(input_values), "end_index": len(input_values)}
                for v in value:
                    input_values.append(v)
                    input_ports[input_port]["end_index"] = len(input_values)
            else:
                input_ports[input_port] = {"index": len(input_values)}
                input_values.append(value)

        header = {
            "ref": ref,
            "task_name": task_name,
            "action": "run_task",
            "input_ports": input_ports,
            "output_ports": output_ports
        }

        self.pending_reference = ref

        self.send(header, *input_values)

        self.pending_reference_event.wait()
        self.pending_reference_event.clear()
        msg = self.pending_reference_message

        returned_output_ports = msg[0]["output_ports"]
        failures = msg[0]["failures"]
        output_values = {}
        for (output_port_name, output_value) in zip(returned_output_ports, msg[1:]):
            output_values[output_port_name] = output_value

        return output_values, failures

    def update_node_metadata(self, node_id: str | None, metadata: dict[str, JsonType] = {},
                             ref: str | None = None) -> None:
        pass

    def set_metadata(self, metadata: dict[str, str], ref: str | None = None):
        raise NotImplementedError()

    def remove_node(self, node_id: str, ref: str | None = None):
        raise NotImplementedError()

    def add_link(self, link_id: str, from_node_id: str, from_port: str | None, to_node_id: str,
                 to_port: str | None, ref: str | None = None):
        raise NotImplementedError()

    def remove_link(self, link_id: str, ref: str | None = None):
        raise NotImplementedError()

    def clear(self, ref: str | None = None):
        raise NotImplementedError()

    def pause(self, ref: str | None = None):
        raise NotImplementedError()

    def resume(self, ref: str | None = None):
        raise NotImplementedError()

    def is_paused(self):
        raise NotImplementedError()

    def restart(self, paused: bool = True, ref: str | None = None):
        raise NotImplementedError()

    def reload_node(self, node_id: str, properties: JsonType, data: dict[str, bytes], ref: str | None = None):
        raise NotImplementedError()

    ####################################################################################################################
    # retrieve node properties and data

    def get_node_properties(self, node_id: str) -> dict[str, JsonType]:
        raise NotImplementedError()

    def get_node_data(self, node_id: str, key: str) -> bytes | None:
        raise NotImplementedError()

    def get_node_data_keys(self, node_id: str) -> list[str]:
        raise NotImplementedError()

    ####################################################################################################################
    # interact with the topology

    def add_output_listener(self, node_id: str, output_port_name: str, listener: Callable[[bytes], None]):
        raise NotImplementedError()

    def remove_output_listener(self, node_id: str, output_port_name: str):
        raise NotImplementedError()

    def inject_input_value(self, node_id: str, input_port_name: str, value: bytes | list[bytes]):
        raise NotImplementedError()

    ####################################################################################################################
    # session and client related

    def open_session(self, session_id: str | None = None) -> str:
        raise NotImplementedError()

    def close_session(self, session_id: str):
        raise NotImplementedError()

    def attach_node_client(self, node_id: str, session_id: str = "", client_id: str = "",
                           client_options: dict = {}) -> ClientApi:
        raise NotImplementedError()

    def attach_configuration_client(self, package_id: str, session_id: str = "", client_id: str = "",
                                    client_options: dict = {}) -> ClientApi:
        raise NotImplementedError()

    ####################################################################################################################
    # load and save

    def load(self, from_file: io.BytesIO, include_data: bool = True):
        raise NotImplementedError()

    def save(self, to_file: io.BufferedWriter = None, include_data: bool = True):
        raise NotImplementedError()

    def import_from(self, from_path: str, include_data: bool = True):
        raise NotImplementedError()

    def export_to(self, to_path: str, include_data: bool = True):
        raise NotImplementedError()

    def serialise(self):
        raise NotImplementedError()

    ####################################################################################################################
    # topology introspection

    def get_nodes(self) -> dict[str, NodeTypeApi]:
        raise NotImplementedError()

    def get_links(self) -> dict[str, tuple[LinkTypeApi, str, str]]:
        raise NotImplementedError()

    def get_link_ids_for_node(self, node_id: str) -> list[str]:
        raise NotImplementedError()

    ####################################################################################################################
    # schema introspection

    def get_schema(self) -> SchemaTypeApi:
        raise NotImplementedError()

    def attach_listener(self, listener: TopologyListenerAPI) -> None:
        self.listeners.append(listener)

    def detach_listener(self, listener: TopologyListenerAPI) -> None:
        self.listeners.remove(listener)

    ####################################################################################################################
    # Internal

    def __create_reference(self):
        return str(uuid.uuid4())
