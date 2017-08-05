import struct

from torrent import Torrent


class PeerConnection(object):

    def __init__(self, file_name):
        self.torrent = Torrent(file_name)


    def announce_tracker(self):
        pass
