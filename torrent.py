import bencoder
from pprint import *


class Torrent(object):

    def __init__(self, file_name):
        file = open(file_name, 'rb')
        self.torrent_data = bencoder.decode(file.read())
        self.info = self.torrent_data[b'info']
        self.announce = self.torrent_data[b'announce']
        self.announce_list = self.torrent_data[b'announce-list']

        self.multi_file = False
        if b'files' in self.info.keys():
            self.multi_file = True
