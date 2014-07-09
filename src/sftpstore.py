import os
import paramiko
import datastore


class SftpStore(datastore.DataStore):
    def exists(self, path):
        if path == "" or path == "/" or path == "./":
            return

        try:
            for f in self.ftp.listdir(os.path.dirname(path)):
                if f == os.path.basename(path):
                    return True
        except IOError:
            pass

        return False

    def makedirs(self, path):
        if path == "" or path == "/" or path == "./":
            return

        if not self.exists(os.path.dirname(path)):
            self.makedirs(os.path.dirname(path))

        if not self.exists(path):
            self.ftp.mkdir(path)

    def store(self, file):
        if self.exists(file):
            self.remove(file)
        elif not self.exists(os.path.dirname(file)):
            self.makedirs(os.path.dirname(file))

        total = os.path.getsize(file)
        trans = 0
        rh = self.ftp.open(file, "wb")
        lh = open(file, "rb")
        byte = lh.read(8192)

        while byte:
            rh.write(byte)
            trans += len(byte)
            self.progress(trans, total)
            byte = lh.read(8192)

        rh.close()
        lh.close()

    def remove(self, file):
        if self.exists(file):
            self.ftp.remove(file)

    def remove_dir(self, dir):
        if self.exists(dir):
            self.ftp.rmdir(dir)

    def __init__(self, synchost):
        datastore.DataStore.__init__(self, synchost)
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        if not self.synchost.username or not self.synchost.password:
            self.synchost.username = None
            self.synchost.password = None

        if not self.synchost.keyfile:
            self.synchost.keyfile = None
        else:
            print "Using key: " + self.synchost.keyfile

        self.ssh.connect(self.synchost.host, port=self.synchost.port,
                         key_filename=self.synchost.keyfile, username=self.synchost.username,
                         password=self.synchost.password)
        self.ftp = self.ssh.open_sftp()

        if not self.exists(self.synchost.path):
            self.makedirs(self.synchost.path)

        self.ftp.chdir(self.synchost.path)