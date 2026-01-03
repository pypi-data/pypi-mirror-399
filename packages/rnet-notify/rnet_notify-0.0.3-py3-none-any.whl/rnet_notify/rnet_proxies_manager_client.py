# This is a sample Python script.
import logging
from math import log
import time
from typing import Optional, Unpack, TYPE_CHECKING
from wsgiref import headers

from rnet import Method, Proxy as ProxyRNet

if TYPE_CHECKING:
    from rnet import ClientConfig, Request

from rnet.blocking import Client, Response
from .proxies_manager import ProxiesManager, Proxy

class RequestErrorException(Exception):
    pass


logger = logging.getLogger(__name__)


class RNetWrapperClient:

    def __init__(self, **kwargs: Unpack["ClientConfig"]):
        self.client_configs = kwargs
        self.client = self._create_client(**kwargs)
        self.emulation = kwargs.get("emulation", None)

    def _create_client(self, **kwargs) -> Client:
        client = Client(**kwargs)
        logger.debug(f"Created new client with configs: {kwargs}")
        return client

    def get_client(self) -> Client:
        return self.client
    
    def execute_request(
            self,
            method: Method,
            url: str,
            **kwargs: Unpack["Request"],
    ) -> "Response":
        try:

            headers = kwargs.get("headers", {})

            start = time.time()
            res = self.client.request(method=method, url=url, **kwargs)
            end = time.time()
            elapsed = end - start

            status_code = res.status.as_int()

            self._create_log(
                method=method,
                request_url=res.url,
                status_code=status_code,
                elapsed=elapsed,
                proxy=None,
                emulation=self.emulation,
                headers=headers
            )

            

            return res
         

        except Exception as e:

            end = time.time()
            elapsed = end - start

            self._create_log(
                method=method,
                request_url=url,
                status_code=-1,
                elapsed=elapsed,
                proxy=None,
                emulation=self.emulation,
                headers=headers
            )

            raise RequestErrorException(e)
        
    def _create_log(self,
                    method: Method,
                    request_url: str,
                    status_code: int,
                    elapsed: float,
                    proxy: Optional[Proxy] = None,
                    emulation: Optional[str] = None,
                    headers: Optional[dict] = None
                    ):
        
        log_parts = [
            f"--- Request Log ---",
            f"Method: {method}",
            f"Proxy: {proxy if proxy else '-'}",
            f"URL: {request_url if request_url else '-'}",
            f"Response Status Code: {status_code if status_code else '-'}",
            f"Emulation: {emulation if emulation else '-'}",
            f"Headers: {headers if headers else '-'}",
            f"Time Taken: {elapsed:.2f} seconds"
        ]

        logger.info("\n".join(log_parts))
        

class RNetProxiesManagerClient(RNetWrapperClient):

    def __init__(self,
                 proxies_manager: ProxiesManager,
                 requests_limit_same_proxy: int = -1,
                 status_codes_to_change_proxy: list[int] = None,
                 **kwargs: Unpack["ClientConfig"]):
        
        super().__init__(**kwargs)
        self.proxies_manager = proxies_manager
        self.requests_limit_same_proxy = requests_limit_same_proxy
        self.status_codes_to_change_proxy = status_codes_to_change_proxy
        self.client_configs = kwargs
        self.client = self._create_client(**kwargs)
        self.requests_made_with_current_proxy = 0


    def get_client(self) -> Client:
        # Logic to select a proxy from the proxies_manager would go here
        # For now, we just create a client with the stored kwargs

        client = self._create_client(**self.client_configs)
        return client
    
    def _is_proxy_change_needed(self, status_code: int, requests_made_with_current_proxy: int) -> bool:

        if self.status_codes_to_change_proxy and status_code in self.status_codes_to_change_proxy:
            return True
        
        if requests_made_with_current_proxy >= self.requests_limit_same_proxy:
            return True
        
        return False

    def execute_request(
            self,
            method: Method,
            url: str,
            **kwargs: Unpack["Request"],
    ) -> "Response":
        try:

            headers = kwargs.get("headers", {})


            start = time.time()

            current_proxy: Proxy = self.proxies_manager.get_current_proxy()
            logger.debug(f"Using proxy: {current_proxy}")
       
            if current_proxy:
                self.requests_made_with_current_proxy += 1
                res = self.client.request(method=method,
                                          url=url,
                                          proxy=ProxyRNet.all(current_proxy.get_proxy_url()),
                                          **kwargs)

            else:
                res = self.client.request(method=method, url=url, **kwargs)

            end = time.time()
            elapsed = end - start

            status_code = res.status.as_int()

            change_proxy = self._is_proxy_change_needed(
                status_code=status_code,
                requests_made_with_current_proxy=self.requests_made_with_current_proxy
            )

            if change_proxy:
                logger.debug(f"Changing proxy due to status code {status_code} "
                             f"or request limit reached ({self.requests_made_with_current_proxy}).")
                
                self.client = self._create_client(**self.client_configs)
                self.proxies_manager.get_next_proxy()
                self.requests_made_with_current_proxy = 0


            self._create_log(
                method=method,
                request_url=url,
                status_code=status_code,
                elapsed=elapsed,
                proxy=current_proxy,
                emulation=self.emulation,
                headers=headers
            )

            return res
         

        except Exception as e:

            self.client = self._create_client(**self.client_configs)
            self.proxies_manager.get_next_proxy()
            self.requests_made_with_current_proxy = 0

            logger.error(f"Request error occurred: {e}. Changed proxy and retrying next request.")

            end = time.time()
            elapsed = end - start

            self._create_log(
                method=method,
                request_url=url,
                status_code=-1,
                elapsed=elapsed,
                proxy=current_proxy,
                emulation=self.emulation,
                headers=headers
            )
            raise RequestErrorException(e)
        
    



