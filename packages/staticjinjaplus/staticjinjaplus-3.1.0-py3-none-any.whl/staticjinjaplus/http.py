from __future__ import annotations
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from typing import Optional
from http import HTTPStatus
from os import fstat, path
import socket


class EnhancedThreadingHTTPServer(ThreadingHTTPServer):
    """Same as ThreadingHTTPServer but the directory to be served may be passed to its constructor. It also tries to
    listen to both IPv4 and IPv6 loopback addresses"""
    allow_reuse_address = True
    daemon_threads = True
    has_dualstack_ipv6: bool
    directory: str
    RequestHandlerClass: SimpleEnhancedHTTPRequestHandler

    def __init__(self, *args, directory: str, **kwargs):
        self.has_dualstack_ipv6 = socket.has_dualstack_ipv6()
        self.address_family = socket.AF_INET6 if self.has_dualstack_ipv6 else socket.AF_INET
        self.directory = directory

        super().__init__(*args, **kwargs)

    def server_bind(self) -> None:
        if self.has_dualstack_ipv6:
            self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)

        super().server_bind()

    def finish_request(self, request, client_address) -> None:
        self.RequestHandlerClass(request, client_address, self, directory=self.directory)


class SimpleEnhancedHTTPRequestHandler(SimpleHTTPRequestHandler):
    """A simple HTTP server handler which is meant to serve the output directory, with some enhancements (emulates URL
    rewrite for HTML files without .html extension; emulates custom 404 error page"""
    protocol_version = 'HTTP/1.1'
    server: EnhancedThreadingHTTPServer

    def __init__(self, *args, **kwargs):
        self.extensions_map.update({
            '.rss': 'application/rss+xml',
            '.atom': 'application/atom+xml',
        })

        try:
            super().__init__(*args, **kwargs)
        except (ConnectionAbortedError, BrokenPipeError):
            pass

    def translate_path(self, p: str) -> str:
        p = super().translate_path(p)

        if not p.endswith(('\\', '/')):
            _, extension = path.splitext(p)

            if not extension:
                p += '.html'

        return p

    def send_error(self, code: int, message: Optional[str] = None, explain: Optional[str] = None) -> None:
        status = HTTPStatus(code)

        if self.command != 'HEAD' and (status.is_client_error or status.is_server_error):
            try:
                f = open(path.join(self.directory, f'{status.value}.html'), 'rb')
            except OSError:
                return super().send_error(code, message=message, explain=explain)

            fs = fstat(f.fileno())

            self.send_response(code, message)
            self.send_header('Connection', 'close')

            self.send_header('Content-Type', self.error_content_type)
            self.send_header('Content-Length', str(fs[6]))
            self.end_headers()

            self.copyfile(f, self.wfile)
        else:
            return super().send_error(code, message=message, explain=explain)
