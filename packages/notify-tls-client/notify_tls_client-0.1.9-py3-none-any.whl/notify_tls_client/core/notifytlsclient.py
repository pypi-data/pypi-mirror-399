import logging
from typing import Optional

from typing_extensions import TypeAlias, Literal

from notify_tls_client.core.client import *
from notify_tls_client.core.client_identifiers_manager import ClientIdentifiersManager
from notify_tls_client.core.proxiesmanager import ProxiesManager, Proxy
from notify_tls_client.tls_client.response import Response
from notify_tls_client.tls_client.sessions import Session
from notify_tls_client.tls_client.settings import ClientIdentifiers
from notify_tls_client.tls_client.structures import CaseInsensitiveDict

HttpMethods: TypeAlias = Literal["GET", "POST", "PUT", "DELETE", "PATCH"]
logger = logging.Logger(__name__)


class NotifyTLSClient:
    def __init__(self,
                 proxies_manager: Optional[ProxiesManager] = None,
                 client_identifiers: list[ClientIdentifiers] = None,
                 requests_limit_same_proxy: int = 1000,
                 random_tls_extension_order: bool = True,
                 requests_limit_with_same_client_identifier: int = -1,
                 instantiate_new_client_on_forbidden_response: bool = False,
                 instantiate_new_client_on_exception: bool = False,
                 debug_mode: bool = False,
                 status_codes_to_forbidden_response_handle: list[int] = None,
                 change_client_identifier_on_forbidden_response: bool = False,
                 default_headers: dict = None,
                 disable_http3: bool = False
                 ):

        self.client: Optional[Session] = None
        self.change_client_identifier_on_forbidden_response = change_client_identifier_on_forbidden_response
        self.client_identifiers_manager = ClientIdentifiersManager(client_identifiers or ["chrome_133"])
        self.status_codes_to_forbidden_response_handle = status_codes_to_forbidden_response_handle or [403]
        self.free = True
        self.requests_amount = 0
        self.requests_amount_with_current_proxy = 0
        self.requests_amount_with_current_client_identifier = 0
        self.last_request_status = 0
        self.headers = default_headers or CaseInsensitiveDict({
            "User-Agent": f"tls-client/1.0.0",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
            "Connection": "keep-alive",
        })

        self.disable_http3 = disable_http3
        self.proxies_manager = proxies_manager
        self.requests_limit_with_same_proxy = requests_limit_same_proxy
        self.requests_limit_with_same_client_identifier = requests_limit_with_same_client_identifier
        self.debug_mode = debug_mode

        self.instantiate_new_client_on_forbidden_response = instantiate_new_client_on_forbidden_response
        self.instantiate_new_client_on_exception = instantiate_new_client_on_exception

        self.current_proxy = None
        self._create_new_client(self.client_identifiers_manager.get_next(),
                                random_tls_extension_order,
                                proxy=self.proxies_manager.get_next() if self.proxies_manager else None)


    def _create_new_client(self,
                           client_identifier: ClientIdentifiers = 'chrome_133',
                           random_tls_extension_order: bool = False,
                           proxy: Optional[Proxy] = None):



        if self.client:
            self.client.close()

        old_client_identifier = self.client.client_identifier if self.client else None

        self.client = Session(client_identifier=client_identifier,
                              random_tls_extension_order=random_tls_extension_order)

        if old_client_identifier != client_identifier:
            self.requests_amount_with_current_client_identifier = 0

        if proxy:

            self.client.proxies = proxy.to_proxy_dict()

            if self.current_proxy != proxy:
                self.current_proxy = proxy
                self.requests_amount_with_current_proxy = 0


    def set_requests_limit_same_proxy(self, requests_limit_same_proxy: int):
        self.requests_limit_with_same_proxy = requests_limit_same_proxy

    def set_proxies_manager(self, proxies_manager: ProxiesManager):
        self.proxies_manager = proxies_manager

    def change_proxy(self):
        if self.proxies_manager and self.proxies_manager.get_proxies():
            self.current_proxy = self.proxies_manager.get_next()
            self.client.proxies = self.current_proxy.to_proxy_dict()
            self.requests_amount_with_current_proxy = 0

    def set_proxies(self, proxies: Proxy):
        self.client.proxies = proxies.to_proxy_dict()

    def set_headers(self, headers: dict):
        self.client.headers = CaseInsensitiveDict(headers)

    def get_cookies(self):
        return self.client.cookies

    def get_cookie_by_name(self, name: str) -> Optional[str]:
        try:
            return self.client.cookies.get(name)
        except Exception as e:
            logging.exception(f"Error getting cookie '{name}': {e}")

    @request_guard_decorator
    def execute_request(self, method: HttpMethods, url: str, **kwargs) -> Optional[Response]:
        method = method.upper()
        if method == "GET":
            return self.client.get(url, **kwargs)
        elif method == "POST":
            return self.client.post(url, **kwargs)
        elif method == "PUT":
            return self.client.put(url, **kwargs)
        elif method == "DELETE":
            return self.client.delete(url, **kwargs)
        elif method == "PATCH":
            return self.client.delete(url, **kwargs)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

    def get(self, url: str, **kwargs) -> Optional[Response]:
        return self.execute_request("GET", url, **kwargs)

    def post(self, url: str, **kwargs) -> Optional[Response]:
        return self.execute_request("POST", url, **kwargs)

    def put(self, url: str, **kwargs) -> Optional[Response]:
        return self.execute_request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs) -> Optional[Response]:
        return self.execute_request("DELETE", url, **kwargs)

    def patch(self, url: str, **kwargs) -> Optional[Response]:
        return self.execute_request("PATCH", url, **kwargs)

    def _change_to_free(self):
        self.free = True

    def _change_to_busy(self):
        self.free = False

    def get_cookie_value_by_name(self, name: str):
        return self.client.cookies.get(name)

    def set_cookie(self, name: str, value: str):
        self.client.cookies.set(name, value)

    def get_tls(self):
        return self.client

    def get_current_client_identifier(self) -> ClientIdentifiers:
        return self.client.client_identifier

    def is_same_proxy_request_limit_reached(self) -> bool:
        if self.requests_limit_with_same_proxy == -1:
            return False

        return self.requests_amount_with_current_proxy >= self.requests_limit_with_same_proxy

    def is_same_client_identifier_request_limit_reached(self) -> bool:
        if self.requests_limit_with_same_client_identifier == -1:
            return False

        return self.requests_amount_with_current_client_identifier >= self.requests_limit_with_same_client_identifier

    def is_client_identifier_changeable_by_requests_limit_reached(self) -> bool:
        return self.is_same_client_identifier_request_limit_reached() and self.has_multiple_client_identifiers()


    def has_multiple_client_identifiers(self) -> bool:
        return self.client_identifiers_manager.get_total_items() > 1


    def is_forbidden_request_status(self, status_code: int) -> bool:
        return status_code in self.status_codes_to_forbidden_response_handle

    def has_proxies_manager(self) -> bool:
        return self.proxies_manager is not None and self.proxies_manager.get_proxies()

    def set_default_headers(self, headers: dict):
        self.headers = headers
        self.client.headers = self.headers
