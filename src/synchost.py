import os
import pickle
from urlparse import urlsplit
import sys
import excepts
import ftpstore
import sftpstore

class SyncHost:
    def get_port(self, url):
        if not url.port:
            if url.scheme == "ftp":
                return 21
            elif url.scheme == "ftps":
                return 21
            elif url.scheme == "sftp":
                return 22

            raise excepts.UrlError("Don't know port for scheme " + url.scheme)

        return url.port

    def parse(self, val):
        schemes = ["ftp", "ftps", "sftp"]
        url = urlsplit(val)

        if not url.scheme in schemes:
            raise excepts.UrlError("Invalid URL scheme in: " + val)

        self.scheme = url.scheme
        self.host = url.hostname
        self.port = self.get_port(url)
        self.path = url.path

        if url.username:
            self.username = url.username

        if url.password:
            self.password = url.password

    def load(self, config):
        data = {}

        if not os.path.isfile(config):
            raise excepts.UsageError("You must initialize a configuration using the --init option with --host first.")

        with open(config, "r") as f:
            data = pickle.load(f)

            if data:
                self.scheme = data["scheme"]
                self.host = data["host"]
                self.port = data["port"]
                self.path = data["path"]
                self.username = data["username"]
                self.password = data["password"]
                self.keyfile = data["keyfile"]
            else:
                sys.stderr.write("Found a config file but failed to load it. Is it valid? Recreate it and try again.")

    def save(self, config):
        data = {}
        data["scheme"] = self.scheme
        data["host"] = self.host
        data["port"] = self.port
        data["path"] = self.path
        data["username"] = self.username
        data["password"] = self.password
        data["keyfile"] = self.keyfile

        if os.path.isfile(config):
            os.remove(config)

        with open(config, "wb") as f:
            pickle.dump(data, f)

    def get_data_store(self):
        if self.scheme == "ftp":
            return ftpstore.FtpStore(self)
        elif self.scheme == "ftps":
            return ftpstore.FtpStore(self)
        elif self.scheme == "sftp":
            return sftpstore.SftpStore(self)

    def __init__(self):
        self.scheme = ""
        self.host = ""
        self.port = 0
        self.path = ""
        self.username = ""
        self.password = ""
        self.keyfile = ""