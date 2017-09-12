import struct
from urllib.parse import  urlparse, urlencode, unquote
import urllib.request as t
import bencoder

from torrent import Torrent


class PeerConnection(object):

    def __init__(self, file_name):
        self.torrent = Torrent(file_name)
        self.announce_tracker()

    def announce_tracker(self):
        payload = self._create_payload()

        print(self.torrent.announce)

        raw_response = t.urlopen(self.torrent.announce.decode() + "?" + payload).read()
        response = bencoder.decode(raw_response)

        if b'failure reason' in response.keys():
            print('Torrent failed because of ' + response[b'failure reason'].decode())
        else:
            print(response)
            print(Torrent.bin_to_dec(response[b'peers']))

    def _create_payload(self):
        payload = dict()
        payload['info_hash'] = struct.pack('!20s', self.torrent.hash_info)
        payload['peer_id'] = struct.pack('!20s', self.torrent.peerID.encode())
        payload['left'] = struct.pack('!q', self.torrent.total_length)
        payload['compact'] = struct.pack('!i', self.torrent.compact)

        # payload['port'] = struct.pack('!i', self.torrent.port)
        # payload['uploaded'] = struct.pack('!q', self.torrent.uploaded)
        # payload['downloaded'] = struct.pack('!q', self.torrent.downloaded)

        return urlencode(payload)


