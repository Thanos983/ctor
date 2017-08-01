from itertools import zip_longest
import bencoder
import random
import hashlib
from binascii import hexlify
from struct import unpack
import requests
from pprint import *


class Torrent(object):
    """ a helper class for keeping track of torrent's information"""

    def __init__(self, file_name):
        file = open(file_name, 'rb')
        self.torrent_data = bencoder.decode(file.read())

        self.info = self.torrent_data[b'info']
        self.announce = self.torrent_data[b'announce']
        self.announce_list = self.torrent_data[b'announce-list']

        self.multi_file = False
        if b'files' in self.info.keys():
            self.multi_file = True

        self.get_peers()

    @staticmethod
    def construct_peer_id():
        return '-PC0001-' + ''.join([str(random.randint(0, 9)) for _ in range(12)])

    def get_total_length(self):
        """ counts and returns the total length of the torrent"""
        length = 0
        if self.multi_file:
            for file in self.info[b'files']:
                length += file[b'length']
        else:
            length = self.info[b'length']

        return length

    @staticmethod
    def grouper(iterable, n, fill_value=None):
        args = [iter(iterable)] * n
        return zip_longest(*args, fillvalue=fill_value)

    def get_peers(self):
        params = dict()

        # encodes and computes sha1 from info
        params['info_hash'] = hashlib.sha1(bencoder.encode(self.info)).digest()
        params['length'] = self.get_total_length()
        params['peerID'] = self.construct_peer_id()

        # response = requests.get(self.announce, params=params)
        response = requests.get(self.announce, params=params)

        response_data = bencoder.decode(response.content)
        pprint(response_data[b'peers'])
        # for peer in self.grouper(response_data[b'peers'], 6):
        #     print(peer)


        print(int.from_bytes(b'\x10;', byteorder='big'))