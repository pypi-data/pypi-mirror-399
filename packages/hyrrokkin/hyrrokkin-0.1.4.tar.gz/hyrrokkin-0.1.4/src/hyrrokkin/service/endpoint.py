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


import os
import threading

import mimetypes

from hyrrokkin.web_server.builtin_server import BuiltinServer

static_folder = os.path.join(os.path.split(__file__)[0], "..", "static")





class Endpoint(threading.Thread):

    def __init__(self, host, port, base_path):
        super().__init__()
        self.daemon = False
        self.host = host
        self.port = port
        self.base_path = base_path
        self.server = BuiltinServer(self.host, self.port)

    def serve_static(self, path, headers, path_parameters, query_parameters, request_body):
        return self.serve_file(os.path.join(static_folder,path_parameters["path"]))

    def serve_file(self, path):
        if os.path.exists(path):
            with open(path, "rb") as f:
                (mimetype, encoding) = mimetypes.guess_type(path)
                content = f.read()
                return (200, content, mimetype, {})
        else:
            return (404, b"NOT FOUND", "text/plain", {})

    def run(self):
        self.server.run()

