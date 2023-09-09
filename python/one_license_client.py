import requests
import random
import threading
import time
import os
import logging
import datetime
from dateutil import parser
import pytz

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


class OneLicenceClient:

    def __init__(self, config):
        self.server_url = config['server_url']
        self.product_id = config['product_id']
        self.version_id = config['version_id']
        self.license_id = config['license_id']
        self.api_counter = 0
        self.sync_retry_counter = 0
        self.consumeUrl = self.server_url + '/products/{}/versions/{}/licenses/{}/consume'.format(
            self.product_id, self.version_id, self.license_id)
        self.clientConnectionId = random.randint(1, 10000000)
        self.activate()

    def activate(self):
        """
        Activate instance
        """
        logging.info('- Activating instance license...')
        response = requests.put(url=self.consumeUrl, json={
                                'type': 'activate',
                                'clientConnectionId': self.clientConnectionId
                                })
        status = response.status_code
        data = response.json()

        if status == 200:
            self.config = data
            logging.info('- Delaying activation for : ' +
                         str(self.config['activationDelay']) + 's')
            time.sleep(self.config['activationDelay'])
            logging.info('- Instance license activated successfully!')
            return
        else:
            raise Exception(data)

    def sync(self):
        """
        Sync client and server
        """
        logging.info('- Consuming single API count')
        response = requests.put(url=self.consumeUrl, json={
                                'type': 'sync',
                                'clientConnectionId': self.clientConnectionId,
                                'apiCallCounter': self.api_counter
                                })
        status = response.status_code
        data = response.json()

        if status == 200:
            self.config = data
            logging.info('- Sync successful')
            self.sync_retry_counter = 0
            self.api_counter = 0
            return
        else:
            logging.error('- Failed to sync')
            raise Exception(data)

    def consume(self):
        """
        Consume single API call
        """
        logging.info('- Consuming single API count')
        self.api_counter += 1

        if self.config['syncTrigger'] == 'AT_EVERY_CALL':
            # When license sync should happen at every API call
            self.sync()
        else:
            # When license sync should happen at fixed intervals
            if self.config['type'] == 'TIME_BOUND_AND_API_CALLS' or self.config['type'] == 'NO_OF_API_CALLS':
                # When license has fixed number of API calls
                if(self.config['apiCallCounter'] + self.api_counter) > self.config['allowedApiCalls']:
                    # When number of API calls has exceeded
                    self.sync()
                    raise Exception('API calls exceeded')
            if self.config['type'] == 'TIME_BOUND_AND_API_CALLS' or self.config['type'] == 'AFTER_INTERVAL':
                # When license is set to expire after a time period
                expiresAt = parser.isoparse(self.config['expiresAt'])
                currentTime = datetime.datetime.now(pytz.UTC)
                if (expiresAt - currentTime).days < 0:
                    self.sync()
                    raise Exception('License has expired')

    def sync_at_interval(self):
        try:
            while True:
                logging.info('- Started periodic license syncing')
                if self.config['syncTrigger'] == 'AFTER_INTERVAL':
                    # For intervalled syncing
                    max_retries = self.config['maxSyncRetries']
                    sync_interval = self.config['syncInterval']
                    interval_bw_retries = sync_interval//max_retries
                    logging.info('- Type : SYNC AFTER INTERVAL')
                    logging.info('- Max retries : ' + str(max_retries))
                    logging.info('- Current retry counter : ' +
                                 str(self.sync_retry_counter))
                    logging.info('- Sync interval : ' +
                                 str(sync_interval) + 's')
                    logging.info('- Interval between retries : ' +
                                 str(interval_bw_retries))

                    if(self.sync_retry_counter >= max_retries):
                        raise Exception('- Max sync retries limit reached.')

                    try:
                        self.sync()
                        logging.info('- Periodic license sync successful')
                        time.sleep(self.config['syncInterval'])
                    except Exception as err:
                        logging.error(err)
                        logging.error('- Sync at interval error!')
                        logging.error('- Retrying sync after: ' +
                                      str(interval_bw_retries) + 's')
                        self.sync_retry_counter += 1
                        time.sleep(interval_bw_retries)
                else:
                    # For per call syncing
                    try:
                        logging.info('- Type : SYNC AT EVERY CALL')
                        logging.info('- Max retries : Infinite')
                        logging.info('- Current retry counter : ' +
                                     str(self.sync_retry_counter))
                        logging.info('- Sync interval : 60s')
                        self.sync()
                        logging.info('- Periodic license sync successful')
                        time.sleep(60)
                    except Exception as err:
                        logging.error('- Sync at interval error!')
                        logging.error('- Retrying sync after: 60s')
                        self.sync_retry_counter += 1
                        time.sleep(60)

        except Exception as err:
            logging.error('- Periodic syncing error')
            logging.error(err)
            logging.error('- Crashing due to licensing error')
            os._exit(1)
