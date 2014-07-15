import ftplib
import os
import datastore


class FtpStore(datastore.DataStore):
    def progress(self, block):
        self.trans_total += len(block)
        datastore.DataStore.progress(self, self.trans_total, self.file_size_total)

    def exists(self, file):
        if file == "" or file == "/" or file == "./":
            return

        try:
            for f in self.ftp.nlst(os.path.dirname(file)):
                if f == os.path.basename(file):
                    return True
        except ftplib.error_perm:
            pass

        return False

    def makedirs(self, path):
        if path == "" or path == "/" or path == "./":
            return

        if not self.exists(os.path.dirname(path)):
            self.makedirs(os.path.dirname(path))

        if not self.exists(path):
            self.ftp.mkd(path)

    def store(self, file):
        self.time = None
        
        if self.exists(file):
            self.remove(file)
        elif not self.exists(os.path.dirname(file)):
            self.makedirs(os.path.dirname(file))

        self.file_size_total = os.path.getsize(file)
        self.trans_total = 0

        with open(file, "rb") as fh:
            self.ftp.storbinary("STOR " + file, fh, 8192, self.progress)

    def remove(self, file):
        if self.exists(file):
            self.ftp.delete(file)

    def remove_dir(self, dir):
        if self.exists(dir):
            self.ftp.rmd(dir)

    def __init__(self, synchost):
        datastore.DataStore.__init__(self, synchost)

        if self.synchost.scheme == "ftp":
            self.ftp = ftplib.FTP()
        elif self.synchost.scheme == "ftps":
            self.ftp = ftplib.FTP_TLS()

        self.ftp.connect(self.synchost.host, self.synchost.port)
        if self.synchost.scheme == "ftps":
            self.ftp.auth()

        self.ftp.login(self.synchost.username, self.synchost.password)
        if self.synchost.scheme == "ftps":
            self.ftp.prot_p()

        if not self.exists(self.synchost.path):
            self.makedirs(self.synchost.path)

        self.ftp.cwd(self.synchost.path)