import logging
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse

from notify_tls_client.tls_client.response import Response

logger = logging.getLogger(__name__)


def __is_valid_url(url: str) -> bool:
    if not isinstance(url, str):
        return False

    parsed = urlparse(url)
    return all([parsed.scheme, parsed.netloc])


def request_guard_decorator(callback):
    def wrapper(*args, **kwargs):
        self = args[0]
        self.free = False
        request_url = None
        request_headers = {}
        res = None

        for arg in args:
            if isinstance(arg, str) and __is_valid_url(arg):
                request_url = arg
                break

        for key, value in kwargs.items():
            if key == 'url':
                request_url = value
                break

            if key == 'headers':
                request_headers = value

        try:
            self.requests_amount += 1
            res = callback(*args, **kwargs)
            _log_request_info(self, res, request_url, request_headers)
            _requests_handler(self, res)
            return res

        except Exception as e:
            logging.exception("Exception occurred during TLS request")
            _log_request_info(self, res, request_url, request_headers)
            _recover_on_exception(self)
            _requests_handler(self, res)

        finally:
            self.free = True

            # _forbidden_request_handler(self, res)

        return None

    return wrapper


def _recover_on_exception(self):
    if self.instantiate_new_client_on_exception:
        logging.info("Instantiating new TLS client due to exception...")
        self.get_tls().close()
        self._create_new_client()

    if self.proxies_manager:
        logging.info("Changing proxy due to exception...")
        self.change_proxy()


def _log_request_info(self,
                      response: Optional[Response],
                      request_url: Optional[str],
                      request_headers: dict):
    if response:
        logger.debug(f"""Request finished
                                        client_identifier={self.get_current_client_identifier()}
                                        request_url={request_url}
                                        request_headers={request_headers}
                                        response_url={response.url}
                                        status_code={response.status_code}
                                        response_time={response.elapsed}ms
                                        response_headers={dict(response.headers)}
                                        proxy={self.client.proxies['http'] if self.client.proxies else None}
                             """,
                     extra={
                         "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S.%f")[:-3],
                         "request_url": request_url,
                         "request_headers": request_headers,
                         "response_url": response.url,
                         "status_code": response.status_code,
                         "response_headers": dict(response.headers),
                         "response_elapsed_ms": response.elapsed,
                         "proxy": self.client.proxies['http'] if self.client.proxies else None,
                         "client_identifier": self.get_current_client_identifier()

                     })

    if not response:
        logger.debug(f"""Request failed before getting a response
                                        client_identifier={self.get_current_client_identifier()}
                                        request_url={request_url}
                                        request_headers={request_headers}
                                        response_url=None
                                        status_code=None
                                        response_headers=None
                                        response_time=0
                                        proxy={self.client.proxies['http'] if self.client.proxies else None}
                             """,
                     extra={
                         "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S.%f")[:-3],
                         "request_url": request_url,
                         "request_headers": request_headers,
                         "response_url": None,
                         "status_code": None,
                         "response_headers": None,
                         "response_elapsed_ms": 0,
                         "proxy": self.client.proxies['http'] if self.client.proxies else None,
                         "client_identifier": self.get_current_client_identifier()

                     })


def _forbidden_request_handler(self, response: Optional[Response]):
    if not response:
        return

    if response.status_code in self.status_codes_to_forbidden_response_handle:
        if self.instantiate_new_client_on_forbidden_response:
            logging.info("Instantiating new TLS client due to forbidden response...")
            self.get_tls().close()
            self._create_new_client()

        if self.proxies_manager:
            logging.info("Changing proxy due to forbidden response...")
            self.change_proxy()


# tem casos que está retornando 403 como erro da API, tenho que estudar o que fazer nesses casos
def _requests_handler(self, response: Optional[Response]):
    self.requests_amount_with_current_client_identifier += 1

    if self.proxies_manager:
        self.requests_amount_with_current_proxy += 1

    if not response:
        return

    client_identifier_changed_by_limit = self.is_client_identifier_changeable_by_requests_limit_reached()
    is_same_proxy_limit = self.is_same_proxy_request_limit_reached()
    is_forbidden_request_status = self.is_forbidden_request_status(response.status_code)
    create_new_client_on_forbidden = self.instantiate_new_client_on_forbidden_response
    change_client_identifier_on_forbidden = self.change_client_identifier_on_forbidden_response
    has_proxies_manager = self.has_proxies_manager()

    if client_identifier_changed_by_limit:
        logging.info("Requests limit reached for current client identifier")
        if is_forbidden_request_status or is_same_proxy_limit:
            self._create_new_client(self.client_identifiers_manager.get_next(),
                                    proxy=None if not has_proxies_manager else self.proxies_manager.get_next())

        else:
            self._create_new_client(self.client_identifiers_manager.get_next(),
                                    proxy=None if not has_proxies_manager else self.proxies_manager.get_current_proxy())

        return

    if is_forbidden_request_status:

        if not create_new_client_on_forbidden:
            if has_proxies_manager:
                logging.info("Changing proxy due to forbidden response...")
                self.change_proxy()

            return

        if create_new_client_on_forbidden:
                if change_client_identifier_on_forbidden:
                    logging.info("Instantiating new TLS client due to forbidden response and changing client identifier...")
                    self._create_new_client(self.client_identifiers_manager.get_next(),
                                            proxy=None if not has_proxies_manager else self.proxies_manager.get_next())

                else:
                    logging.info("Instantiating new TLS client due to forbidden response...")
                    item = self.client_identifiers_manager.get_current_item()
                    self._create_new_client(str(item),
                                            proxy=None if not has_proxies_manager else self.proxies_manager.get_next())


    if is_same_proxy_limit:
        if has_proxies_manager:
            logging.info("Changing proxy due to requests limit reached...")
            self.change_proxy()

    # if client_identifier_changed_by_limit:
    #     logging.info("Requests limit reached for current client identifier")
    #     logging.info("Changing client identifier due to requests limit reached...")
    #     # self._create_new_client(self.client_identifiers_manager.get_next(),
    #     #                         proxy=self.proxies_manager.get_current_proxy() if self.proxies_manager else None)
    #
    #
    #
    #
    # if self.requests_limit_with_same_proxy and self.requests_amount_with_current_proxy >= self.requests_limit_with_same_proxy:
    #     logging.info("Requests limit reached for current proxy")
    #     if self.proxies_manager:
    #         proxy_changed_by_limit = True
    #         logging.info("Changing proxy due to requests limit reached...")
    #
    #         if response.status_code in self.status_codes_to_forbidden_response_handle and self.instantiate_new_client_on_forbidden_response:
    #             logging.info("Instantiating new TLS client due to forbidden response before changing proxy...")
    #             self.get_tls().close()
    #             if self.change_client_identifier_on_forbidden_response:
    #                 self._create_new_client(self.client_identifiers_manager.get_next())
    #             else:
    #                 self._create_new_client(self.client_identifiers_manager.get_current())
    #
    #         self.change_proxy()
    #
    # # Metodo vai ter que ser usado para não trocar o proxy duas vezes, uma pelo status 403 e outra pelo limite de requests
    # if not proxy_changed_by_limit:
    #     return
    #
    # if response.status_code in self.status_codes_to_forbidden_response_handle:
    #     if self.instantiate_new_client_on_forbidden_response:
    #         logging.info("Instantiating new TLS client due to forbidden response...")
    #         self.get_tls().close()
    #
    #         if self.change_client_identifier_on_forbidden_response:
    #             self._create_new_client(self.client_identifiers_manager.get_next())
    #         else:
    #             self._create_new_client()
    #
    #     if self.proxies_manager:
    #         logging.info("Changing proxy due to forbidden response...")
    #         self.change_proxy()
