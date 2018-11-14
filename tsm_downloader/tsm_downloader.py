#!/usr/bin/python3
"""
TSM Downloader
==============
A program to save XML traffic data from the given URL to an sqlite3 database, for the TSM project,
more info at `https://github.com/adbenitez/tsm`_

.. note::

   To crawl periodically use cron or similar.

"""
from logging.handlers import RotatingFileHandler
import argparse
import gzip
import logging
import itertools
import os
import shutil
import socket
import sqlite3
import sys
import urllib.request
import xml.etree.ElementTree as ET


__version__ = '0.0.0a0'
__author__ = 'adbenitez'


class RollingGzipFileHandler(RotatingFileHandler):
    # override
    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        for i in itertools.count(1):
            nextName = "%s.%d.gz" % (self.baseFilename, i)
            if not os.path.exists(nextName):
                with open(self.baseFilename, 'rb') as original_log:
                    with gzip.open(nextName, 'wb') as gzipped_log:
                        shutil.copyfileobj(original_log, gzipped_log)
                os.remove(self.baseFilename)
                break
        if not self.delay:
            self.stream = self._open()


class DBManager:
    tokens = [
        'HK', 'K', 'TM', 'ST',
        'MAJOR ROUTE', 'URBAN ROAD',
        'TRAFFIC GOOD', 'TRAFFIC AVERAGE', 'TRAFFIC BAD']

    def __init__(self, logger, db_path):
        self.logger = logger
        self.conn = sqlite3.connect(db_path)
        self.cur = self.conn.cursor()
        self.init_tables()

    def init_tables(self):
        self.cur.execute('''CREATE TABLE IF NOT EXISTS code
        (id INTEGER NOT NULL,
        value TEXT NOT NULL,
        PRIMARY KEY(id))''')
        code_count = self.cur.execute('SELECT COUNT(*) from code').fetchone()[0]
        if code_count == 0:
            for i, c in enumerate(self.tokens):
                self.cur.execute('INSERT INTO code VALUES (?,?)', (i,c))
        self.cur.execute('''CREATE TABLE IF NOT EXISTS link
        (start INTEGER NOT NULL,
        end INTEGER NOT NULL,
        region INTEGER NOT NULL CHECK(region IN (0,1,2,3)),
        rt INTEGER NOT NULL CHECK(rt IN (4,5)),
        PRIMARY KEY(start, end))''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS capture
        (link_start INTEGER NOT NULL REFERENCES link(start),
        link_end INTEGER NOT NULL REFERENCES link(end),
        rsl INTEGER NOT NULL CHECK (rsl IN (6,7,8)),
        ts REAL NOT NULL,
        date TEXT NOT NULL,
        PRIMARY KEY (link_start, link_end, date))''')

    def save_data(self, data):
        root = ET.fromstring(data)
        ns = {'td': 'http://data.one.gov.hk/td'}
        link_count = self.cur.execute('SELECT COUNT(*) from link').fetchone()[0]
        for e in root:
            link_start, link_end = [int(l) for l
                                    in e.find('td:LINK_ID', ns).text.split('-')]
            if link_count == 0:  # populate link table only if it was empty
                region = self.tokens.index(e.find('td:REGION', ns).text)
                rt = self.tokens.index(e.find('td:ROAD_TYPE', ns).text)
                self.cur.execute('INSERT INTO link VALUES (?,?,?,?)',
                                 (link_start, link_end, region, rt))
            rsl = self.tokens.index(e.find('td:ROAD_SATURATION_LEVEL', ns).text)
            ts = float(e.find('td:TRAFFIC_SPEED', ns).text)
            date = e.find('td:CAPTURE_DATE', ns).text
            capture_row = (link_start, link_end, rsl, ts, date)
            try:
                self.cur.execute('INSERT INTO capture VALUES (?,?,?,?,?)',
                                 capture_row)
            except sqlite3.IntegrityError as e:
                self.logger.error("%s %s", e, capture_row)


def create_args_parser():
    p = argparse.ArgumentParser(
        description='TSM Downloader',
        epilog='Send bugs and suggestions to <https://github.com/adbenitez/tsm/issues>')
    p.add_argument('--version', action='version', version=__version__)
    g = p.add_mutually_exclusive_group()
    g.add_argument('--imp', metavar='PATH',
                   help='import into the database the given XML file or directory containing XML files')
    g.add_argument('--url',
                   help='URL to the xml data (default: %(default)s)',
                   default='http://resource.data.one.gov.hk/td/speedmap.xml')
    p.add_argument('--db', required=True, help='path to the database file')
    p.add_argument('--log', required=True, help='path to the log file')
    p.add_argument('--log-maxbytes', default=10000000, type=int, metavar='NUM',
                   help='the maximum number of bytes the log file can have before moving it to a backup file (default: %(default)s)')
    p.add_argument('--timeout', type=int, default=30,
                   help='the URL request timeout in seconds (default: %(default)s)')
    p.add_argument('--debug', store=True, help='store debug info in the log file')
    return p


def create_logger(log_path, max_size, debug):
    logger = logging.Logger("tsm-downloader")
    logger.parent = None
    fhandler = RollingGzipFileHandler(log_path, maxBytes=max_size)
    if debug:
        fhandler.setLevel(logging.DEBUG)
    else:
        fhandler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s')
    fhandler.setFormatter(formatter)
    logger.addHandler(fhandler)
    return logger


def get_paths(path):
    paths = []
    if os.path.isfile(path):
        paths.append(path)
    elif os.path.isdir(path):
        paths = [os.path.join(r, f)
                 for r, _, files in os.walk(path) for f in files]
    return paths


def main():
    args = create_args_parser().parse_args()
    logger = create_logger(args.log, args.log_maxbytes, args.debug)
    try:
        dbm = DBManager(logger, args.db)
        if args.imp:
            paths = get_paths(args.imp)
            if not paths:
                logger.error("Can't import %s.", args.imp)
                sys.exit(1)
            for p in paths:
                with open(p) as fd:
                    logger.debug('Importing: %s', p)
                    dbm.save_data(fd.read())
        else:
            socket.setdefaulttimeout(args.timeout)
            with urllib.request.urlopen(args.url) as resp:
                dbm.save_data(resp.read())
        dbm.conn.commit()
    except Exception as e:
        logger.exception(e)
    finally:
        dbm.conn.close()


if __name__ == '__main__':
    main()
