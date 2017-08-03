import bencoder
import random
import hashlib
import socket
from struct import unpack
import twisted
import requests
from pprint import pprint

class Torrent(object):
    """ a helper class for keeping track of torrent's information"""

    def __init__(self, file_name):
        file = open(file_name, 'rb')
        self.torrent_data = bencoder.decode(file.read())
        self.peerID = self.construct_peer_id()

        self.downloaded = 0
        self.uploaded = 0
        self.compact = 1
        self.port = 6882
        self.event = 'started'
        self.info = self.torrent_data[b'info']
        self.announce = self.torrent_data[b'announce']
        # self.announce_list = self.torrent_data[b'announce-list']

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

    # @staticmethod
    # def grouper(iterable, n, fill_value=None):
    #     args = [iter(iterable)] * n
    #     return zip_longest(*args, fillvalue=fill_value)

    def get_peers(self):
        params = dict()

        # encodes and computes sha1 from info
        params['info_hash'] = hashlib.sha1(bencoder.encode(self.info)).digest()
        params['peerID'] = self.peerID
        params['port'] = self.port
        params['uploaded'] = self.uploaded
        params['downloaded'] = self.downloaded
        params['length'] = self.get_total_length()
        params['compact'] = self.compact
        params['event'] = self.event

        # send get request to the tracker
        response = requests.get(self.announce, params=params)
        print(params)
        print(response.url)

        response_data = bencoder.decode(response.content)
        print(response_data)
        # response_data[b'peers'] = self.bin_to_dec(response_data[b'peers'])

        # handshake_response = self._handshake(response_data[b'peers'])

        return response_data

    @staticmethod
    def bin_to_dec(peers):
        """
        Take a list of peers into binary form and transform it into dec
        :param peers:
        :return: a list of peers in decimal
        """
        # splits the binary string into a list of binary strings with 6 digits length
        peers = [peers[i:i+6] for i in range(0, len(peers), 6)]

        # translates each binary string into decimal ip:port and returns it
        return [(socket.inet_ntoa(p[:4]), unpack(">H", p[4:])[0]) for p in peers]

    def _handshake(self, peers):
        params = dict()

        # encodes and computes sha1 from info
        params['protocol_len'] = chr(19)
        params['protocol'] = b'BitTorrent protocol'
        params['reserved'] = 8 * chr(0)
        params['peerID'] = self.peerID
        params['info_hash'] = hashlib.sha1(bencoder.encode(self.info)).digest()

        # send get request to the tracker
        response = requests.get(self.announce, params=params)
        print(response.url)

        response_data = bencoder.decode(response.content)
        response_data[b'peers'] = self.bin_to_dec(response_data[b'peers'])
        print(response_data)

        return response_data


class PeerConnection(object):
    pass