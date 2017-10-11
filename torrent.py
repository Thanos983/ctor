import bencoder
import random
import hashlib
import socket
from urllib import parse
from struct import unpack


class Torrent(object):
    """ a helper class for keeping track of torrent's information"""

    @staticmethod
    def magnet_to_torrent(magnet):
        """ Retrieves the necessary information from the magnet link"""
        torrent_data = dict()
        announce_list = list()
        info = dict()
        magnet = magnet[8::].split("&")
        magnet = [element.split('=') for element in magnet]
        print(magnet)

        for element in magnet:
            if element[0] == 'xt':
                info[b'hash_info'] = element[1][9::].encode()
            elif element[0] == 'dn':
                info[b'name'] = element[1]
            elif element[0] == 'tr':
                if b'announce' not in torrent_data.keys():  # announce is empty
                    torrent_data[b'announce'] = parse.unquote(element[1]).encode()
                else:  # Announce has a link already. Populate announce list
                    announce_list.append(parse.unquote(element[1]).encode())

        torrent_data[b'info'] = info
        torrent_data[b'announce-list'] = announce_list
        torrent_data[b'creation date'] = None
        print(torrent_data)

        return torrent_data

    def __init__(self, file_name):

        self.file_name = file_name
        self.peerID = self.construct_peer_id()
        self.downloaded = 0
        self.uploaded = 0
        self.compact = 1
        # TODO: proper handling of port. From 6881-6889 check every port if it is open and pick the first one
        self.port = 6882
        # self.event = 'started'

        if file_name.endswith('torrent'):
            file = open(file_name, 'rb')
            self.torrent_data = bencoder.decode(file.read())
            self.info = self.torrent_data[b'info']
            self.hash_info = hashlib.sha1(bencoder.encode(self.info)).digest()

            self.creation_date = self.torrent_data[b'creation date']
            self.announce_list = list()

            if b'announce_list' in self.torrent_data.keys():
                self.announce_list = self.torrent_data[b'announce-list']
            elif b'httpseeds' in self.torrent_data.keys():
                self.announce_list = self.torrent_data[b'httpseeds']

            self.announce_list.append(self.torrent_data[b'announce'])

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

        elif file_name.startswith('magnet'):
            self.torrent_data = self.magnet_to_torrent(file_name)
            self.hash_info = self.torrent_data[b'info'][b'hash_info']
            self.announce_list = self.torrent_data[b'announce-list']
            self.announce_list.append(self.torrent_data[b'announce'])

    @staticmethod
    def construct_peer_id():
        return '-PC0001-' + ''.join([str(random.randint(0, 9)) for _ in range(12)])

    def get_total_length(self):
        """ counts and returns the total length of the torrent"""
        length = 0
        for file in self.files:
            length += file[b'length']

        return length

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
