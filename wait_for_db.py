"""
Django management command wait_for_database
"""
import sys
from time import sleep, time
from pymongo import MongoClient, collection

from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.utils import OperationalError


def wait_for_database(**opts):
    """
    The main loop waiting for the database connection to come up.
    """
    wait_for_db_seconds = opts['wait_when_down']
    alive_check_delay = opts['wait_when_alive']
    stable_for_seconds = opts['stable']
    timeout_seconds = opts['timeout']
    db_alias = opts['database']

    conn_alive_start = None
    client = MongoClient()
    
    start = time()

    while True:
        # loop until we have a database connection or we run into a timeout
        while True:
            try:
                db = client[db_alias]
                col = self.get_collection(collection_names['chats'])
                col.find_one()   
                if not conn_alive_start:
                    conn_alive_start = time()
                break
            except Error as err:
                conn_alive_start = None

                elapsed_time = int(time() - start)
                if elapsed_time >= timeout_seconds:
                    raise TimeoutError(
                        'Could not establish database connection.'
                    ) from err

                err_message = str(err).strip()
                print(f'Waiting for database (cause: {err_message}) ... '
                      f'{elapsed_time}s',
                      file=sys.stderr, flush=True)
                sleep(wait_for_db_seconds)

        uptime = int(time() - conn_alive_start)
        print(f'Connection alive for > {uptime}s', flush=True)

        if uptime >= stable_for_seconds:
            break

        sleep(alive_check_delay)



        """
        Wait for a database connection to come up. Exit with error
        status when a timeout threshold is surpassed.
        """
try:
    wait_for_database(**options)
except TimeoutError as err:
    raise Error(err) from err