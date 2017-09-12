import bencoder
import random
import hashlib
import socket
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
        # print(magnet)

        for element in magnet:
            if element[0] == 'xt':
                info[b'hash_info'] = element[1][9::]
            elif element[0] == 'dn':
                info[b'name'] = element[1]
            elif element[0] == 'tr':
                if b'announce' not in torrent_data.keys():  # announce is empty
                    torrent_data[b'announce'] = element[1]
                else:  # Announce has a link already. Populate announce list
                    announce_list.append(list(element[1]))

        torrent_data[b'info'] = info
        torrent_data[b'announce-list'] = announce_list
        torrent_data[b'creation date'] = None

        return torrent_data

    def __init__(self, file_name):

        if file_name.endswith('torrent'):
            file = open(file_name, 'rb')
            self.torrent_data = bencoder.decode(file.read())
            self.info = self.torrent_data[b'info']
            self.hash_info = hashlib.sha1(bencoder.encode(self.info)).digest()
        elif file_name.startswith('magnet'):
            self.torrent_data = self.magnet_to_torrent(file_name)
            self.hash_info = self.torrent_data[b'info'][b'hash_info']

        # print(self.torrent_data)

        self.peerID = self.construct_peer_id()
        self.downloaded = 0
        self.uploaded = 0
        self.compact = 1
        # TODO: proper handling of port. From 6881-6889 check every port if it is open and pick the first one
        self.port = 6882
        self.event = 'started'

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
        # self.get_udp_peers()

    # def get_udp_peers(self):
    #
    #     key = int(random.randrange(0, 255)) #  transaction key
    #     action = 0x0
    #
    #     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #     hostname = urlparse(self.announce).hostname
    #     port = urlparse(self.announce).port
    #
    #     sock.settimeout(8)
    #     conn = (socket.gethostbyname(hostname), port)
    #
    #     req, transaction_id = self.udp_create_connection()
    #     print(type(req), type(conn))
    #     sock.sendto(req, conn)
    #     buf = sock.recvfrom(2048)[0]
    #     connection_id = self.udp_parse_connection_response(buf, transaction_id)
    #     print(connection_id)
    #
    #     payload = struct.pack("!q", connection_id)  # first 8 bytes is connection id
    #     payload += struct.pack("!i", action)
    #     payload += struct.pack("!i", transaction_id)  # followed by 4 byte transaction id
    #     payload += struct.pack('!20s', hashlib.sha1(bencoder.encode(self.info)).digest())
    #     payload += struct.pack('!20s', self.peerID.encode())
    #     payload += struct.pack('!q', int(self.downloaded))
    #     payload += struct.pack('!q', int(self.total_length))
    #     payload += struct.pack('!q', int(self.uploaded))
    #     payload += struct.pack("!i", 0x2)  # event 2 denotes start of downloading
    #     payload += struct.pack("!i", 0x0)
    #     payload += struct.pack("!i", key)
    #     payload += struct.pack("!i", -1)  # Number of peers required. Set to -1 for default
    #     payload += struct.pack('!q', sock.getsockname()[1])  # port that got the answer
    #
    #     sock.sendto(payload, conn)
    #
    #     response = sock.recvfrom(2048)[0]
    #     print(response)

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

    def _handshake(self):
        params = dict()

        # encodes and computes sha1 from info
        params['protocol_len'] = chr(19)
        params['protocol'] = b'BitTorrent protocol'
        params['reserved'] = 8 * chr(0)
        params['peerID'] = self.peerID
        params['info_hash'] = hashlib.sha1(bencoder.encode(self.info)).digest()
