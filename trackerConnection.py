import struct
from urllib.parse import  urlparse, urlencode, unquote
import urllib.request as t
import urllib.error
import bencoder

from torrent import Torrent


class PeerConnection(object):

    def __init__(self, file_name):
        self.torrent = Torrent(file_name)
        self.announce_tracker()

    def announce_tracker(self):
        """
        Gets the list of peers from the tracker
        :return: list of peers
        """

        payload = self._create_payload()

        print(self.torrent.file_name)

        for url_tracker in self.torrent.announce_list:

            if url_tracker.startswith(b'udp'):
                url_tracker = b'http' + url_tracker

            print(url_tracker)

            try:
                raw_response = t.urlopen(url_tracker.decode() + "?" + payload).read()
                response = bencoder.decode(raw_response)

                if b'failure reason' in response.keys():
                    print('Torrent failed because of ' + response[b'failure reason'].decode())
                else:
                    # print(response)
                    print(Torrent.bin_to_dec(response[b'peers']))

            except urllib.error.URLError as e:
                print(e)

        print()

    def _create_payload(self):
        """
        Created the information to sent to tracker in order to get the list of peers
        :return Dict with the info to be send:
        """
        payload = dict()
        payload['info_hash'] = struct.pack('!20s', self.torrent.hash_info)
        payload['peer_id'] = struct.pack('!20s', self.torrent.peerID.encode())
        # payload['left'] = struct.pack('!q', self.torrent.total_length)
        payload['left'] = struct.pack('!q', 2350)
        payload['compact'] = struct.pack('!i', self.torrent.compact)

        # payload['port'] = struct.pack('!i', self.torrent.port)
        # payload['uploaded'] = struct.pack('!q', self.torrent.uploaded)
        # payload['downloaded'] = struct.pack('!q', self.torrent.downloaded)

        return urlencode(payload)


