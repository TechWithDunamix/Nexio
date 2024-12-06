from typing import Any, Dict, Optional, Union, List, AsyncGenerator, Callable, Tuple, Protocol
import json
from urllib.parse import parse_qs
from .cookies_parser import parse_cookies
from .parsers import parse_multipart_data,parse_form_urlencoded
from ..structs import URL,State,Headers
from .mixins import RequestValidatonMixin
SERVER_PUSH_HEADERS_TO_COPY = {
    "accept",
    "accept-encoding",
    "accept-language",
    "cache-control",
    "user-agent",
}

class ClientDisconnect(Exception):
    """Custom exception to indicate client disconnection."""
    pass

class HTTPConnection:
    """Base class for managing HTTP connections, including 
        headers, cookies, and client details.
    """
    def __init__(self, scope: Dict[str, Any]) -> None:
        self.scope = scope
        
    @property
    def url(self) -> URL:
        return URL(scope=self.scope)

    def build_absolute_uri(self, path: Optional[str] = None) -> str:
        base_url = self.url.rsplit("?", 1)[0]  # Remove query if exists
        if path:
            return f"{base_url.rstrip('/')}/{path.lstrip('/')}"
        return base_url

    @property
    def headers(self) -> Dict[str, str]:
        return Headers({name.decode(): value.decode() for name, value in self.scope.get("headers", [])})

    @property
    def cookies(self) -> Dict[str, str]:
        """Parses and returns cookies from headers."""
        cookie_header = self.headers.get("cookie", "")
        return parse_cookies(cookie_header)

    @property
    def content_type(self) -> str:
        """Returns the MIME type of the request content."""
        content_type_header = self.headers.get("content-type", "")
        content_type, _ = self._parse_content_type(content_type_header)
        return content_type

    def _parse_content_type(self, content_type_header: str) -> Tuple[str, Dict[str, str]]:
        """Parses the 'Content-Type' header into MIME type and any additional parameters."""
        if not content_type_header:
            return "", {}
        
        main_type, *params = content_type_header.split(";")
        params_dict = {}
        for param in params:
            if "=" in param:
                key, value = param.strip().split("=", 1)
                params_dict[key] = value.strip('"')
        return main_type.strip().lower(), params_dict

    @property
    def client(self) -> Optional[Tuple[str, int]]:
        """Returns client information as a tuple of (host, port)."""
        return self.scope.get("client")

    def get_header(self, name: str) -> Optional[str]:
        """Fetches a single header by name, case-insensitive."""
        return self.headers.get(name.lower())

    @property
    def user_agent(self) -> str:
        """Returns the User-Agent header if available."""
        return self.headers.get("user-agent", "")

    @property
    def query_params(self) -> Dict[str, Union[str, List[str]]]:
        """
        Parses and returns the query parameters from the URL as a dictionary.
        Each key is a query parameter, and the values are either a string or a list of strings
        (if the parameter is repeated in the query string).
        """
        query_string = self.scope.get("query_string", b"").decode("utf-8")
        return {key: value[0] if len(value) == 1 else value 
                for key, value in parse_qs(query_string).items()}
    @property
    def base_url(self) -> URL:
        if not hasattr(self, "_base_url"):
            base_url_scope = dict(self.scope)
            
            app_root_path = base_url_scope.get("app_root_path", base_url_scope.get("root_path", ""))
            path = app_root_path
            if not path.endswith("/"):
                path += "/"
            base_url_scope["path"] = path
            base_url_scope["query_string"] = b""
            base_url_scope["root_path"] = app_root_path
            self._base_url = URL(scope=base_url_scope)
        return self._base_url
    @property
    def state(self) -> State:
        if not hasattr(self, "_state"):
            # Ensure 'state' has an empty dict if it's not already populated.
            self.scope.setdefault("state", {})
            # Create a state instance with a reference to the dict in which it should
            # store info
            self._state = State(self.scope["state"])
        return self._state
class Request(HTTPConnection, RequestValidatonMixin):
    """Handles HTTP request data with improved data parsing capabilities."""
    
    def __init__(self, scope: Dict[str, Any], receive: Callable[[], bytes], send: Callable) -> None:
        super().__init__(scope)
        self._receive = receive
        self._body = None
        self._json_data = None
        self._form_data = None
        self._parsed_data = None
        self._files = None
        self.scope = scope
        self._receive = receive
        self._send = send
        self.user = None
      

    @property
    async def body(self) -> bytes:
        """Asynchronously retrieves the raw request body."""
        if self._body is None:
            self._body = b""
            message = await self._receive()
            if message["type"] == "http.request":
                self._body += message.get("body", b"")
        return self._body

    @property
    async def json(self) -> Dict[str, Any]:
        """
        Parses and returns JSON data from the body.
        Returns empty dict if body is not valid JSON.
        """
        if self._json_data is None:
            try:
                body = await self.body
                self._json_data = json.loads(body.decode('utf-8'))
                if not isinstance(self._json_data,dict):
                    self._json_data = {}
            except (json.JSONDecodeError, UnicodeDecodeError):
                self._json_data = {}
        return self._json_data

    @property
    async def form_data(self) -> Dict[str, Any]:
        """
        Parses and returns form data from the body.
        Handles both multipart/form-data and application/x-www-form-urlencoded.
        """
        if self._form_data is None:
            content_type = self.content_type.lower()
            
            if content_type == 'multipart/form-data':
                self._form_data = {}
                multipart_data = await parse_multipart_data(self)
                # Separate files and form fields
                for key, value in multipart_data.items():
                    if hasattr(value, 'filename'):  # It's a file
                        if self._files is None:
                            self._files = {}
                        self._files[key] = value
                    else:  # It's a form field
                        self._form_data[key] = value
                        
            elif content_type == 'application/x-www-form-urlencoded':
                body = await self.body
                body_str = body.decode('utf-8')
                self._form_data = parse_form_urlencoded(body_str)
            else:
                self._form_data = {}
                
        return self._form_data

    @property
    async def files(self) -> Dict[str, Any]:
        """Always re-fetch the files from the body."""
        if self.content_type.lower() == 'multipart/form-data':
            multipart_data = await parse_multipart_data(self)
            files = {}
            for key, value in multipart_data.items():
                if hasattr(value, 'filename'):  # It's a file
                    files[key] = value
            return files
        return {}


    @property
    async def data(self) -> Dict[str, Any]:
        """
        Returns all parsed data from the request body, combining:
        - JSON data (if content-type is application/json)
        - Form data (if content-type is multipart/form-data or x-www-form-urlencoded)
        """
        if self._parsed_data is None:
            content_type = self.content_type.lower()
            
            if content_type == 'application/json':
                self._parsed_data = await self.json
            elif content_type in ['multipart/form-data', 'application/x-www-form-urlencoded']:
                self._parsed_data = await self.form_data
            else:
                self._parsed_data = {}
                
        return self._parsed_data
    
    @property
    def method(self) -> str:
        """Returns the HTTP method (GET, POST, etc.)."""
        return self.scope["method"]

    async def stream(self) -> AsyncGenerator[bytes, None]:
        """Asynchronously yields chunks of the request body for streaming."""
        message = await self._receive()
        if message["type"] == "http.request":
            yield message.get("body", b"")
        elif message["type"] == "http.disconnect":
            raise ClientDisconnect()

    async def is_disconnected(self) -> bool:
        """Checks if the client has disconnected."""
        message = await self._receive()
        return message.get("type") == "http.disconnect"

    async def send_push_promise(self, path: str) -> None:
        if "http.response.push" in self.scope.get("extensions", {}):
            raw_headers: list[tuple[bytes, bytes]] = []
            for name in SERVER_PUSH_HEADERS_TO_COPY:
                for value in self.headers.getlist(name):
                    raw_headers.append((name.encode("latin-1"), value.encode("latin-1")))
            await self._send({"type": "http.response.push", "path": path, "headers": raw_headers})