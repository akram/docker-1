# -*- coding: utf-8 -*-
import requests_cache
import logging
import requests
import ssl
import time

logger = logging.getLogger(__name__)
ssl._create_default_https_context = ssl._create_unverified_context


# Docker api
#
class DockerApi():
    retries = 0

    def __init__(self, no_cache, debug):
        """Constructor

        @param no_cache: Disable cache
        @type no_cache: bool
        @param debug: Is debug mode enabled
        @type debug: bool
        """
        self.sleep_time = 1
        self.url = 'https://hub.docker.com/v2/repositories/prestashop/prestashop'
        self.no_cache = no_cache
        self.is_debug = debug

        if not self.no_cache:
            requests_cache.install_cache('cache')

    def get_tags(self):
        """Generate return tags

        @return: The json content
        @rtype: dict

        """
        logger.debug(
            'Processing request for tags'
        )

        data = self.execute(
            self.url + '/tags'
        )

        return data['results']

    def execute(self, request_url):
        """Execute url

        @param request_url: The url to execute
        @return: The HTTP Response
        @rtype: dict
        """
        logger.debug(
            'Execute URL: ' + request_url
        )

        resp = requests.get(
            request_url
        )

        data = resp.json()

        if resp.status_code != 200:
            # Something went wrong, retry
            time.sleep(self.sleep_time)
            DockerApi.retries += 1
            if DockerApi.retries >= 10:
                raise requests.HTTPError(resp.text)

            return self.execute(request_url)
        else:
            DockerApi.retries = 0
            # Data not in cache
            if not hasattr(resp, 'from_cache') or not resp.from_cache:
                time.sleep(self.sleep_time)

            if 'next' in data and data['next'] is not None:
                # Compute items if there is a next url
                data['results'] += self.execute(
                    data['next']
                )['results']
        return data
