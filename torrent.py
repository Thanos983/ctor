import bencoder
import random
import hashlib
import json
import requests
import socket
from struct import unpack
from urllib.parse import urlparse
from pprint import pprint


class Torrent(object):
    """ a helper class for keeping track of torrent's information"""

    def __init__(self, file_name):

        file = open(file_name, 'rb')
        self.torrent_data = bencoder.decode(file.read())
        print(self.torrent_data)

        self.peerID = self.construct_peer_id()
        self.downloaded = 0
        self.uploaded = 0
        self.compact = 1
        # TODO: proper handling of port. From 6881-6889 check every port if it is open and pick the first one
        self.port = 6882
        self.event = 'started'
        self.info = self.torrent_data[b'info']
        self.creation_date = self.torrent_data[b'creation date']
        self.announce = self.torrent_data[b'announce']

        if b'announce_list' in self.torrent_data.keys():
            self.announce_list = self.torrent_data[b'announce-list']
        elif b'httpseeds' in self.torrent_data.keys():
            self.announce_list = self.torrent_data[b'httpseeds']

        if b'files' in self.info.keys():
            self.files = self.info[b'files']
        else:
            # In case we have only one file we change it to a similar format as multi file torrent
            self.files = list()
            file_data = dict()
            file_data[b'length'] = self.info[b'length']
            file_data[b'path'] = list()
            file_data[b'path'].append(self.info[b'name'])
            self.files.append(file_data)

        self.total_length = self.get_total_length()



    @staticmethod
    def construct_peer_id():
        return '-PC0001-' + ''.join([str(random.randint(0, 9)) for _ in range(12)])

    def get_total_length(self):
        """ counts and returns the total length of the torrent"""
        length = 0
        for file in self.files:
            length += file[b'length']

        return length

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

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}
        # send get request to the tracker
        MAX_RETRIES = 20
        session = requests.session()
        print(self.announce)
        # adapter = requests.adapters.HTTPAdapter(max_retries=MAX_RETRIES)
        # session.mount('https://', adapter)
        # session.mount('http://', adapter)

        response = session.get('http://atrack.pow7.com/announce', params=params, verify=False, timeout=3)
        print(response)
        response_data = bencoder.decode(response.content)
        try:
            response_data[b'peers'] = self.bin_to_dec(response_data[b'peers'])
        except KeyError:
            print("torrent " + str(self.info[b'name']) + ' could not be downloaded')

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



class PeerConnection(object):
    pass