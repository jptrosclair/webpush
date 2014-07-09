import os
import sys
import hashlib


class SyncFolder:
    def get_hash_path(self, file):
        if file[0:2] == "./":
            return os.path.join(self.app.HASH_DIR, file[2:])
        return os.path.join(self.app.HASH_DIR, file)

    def get_hash(self, file):
        hash = hashlib.sha256()

        with open(file, "rb") as fh:
            while 1:
                buf = fh.read(8192)
                if len(buf) > 0:
                    hash.update(buf)
                else:
                    break

        return hash.hexdigest()

    def get_old_hash(self, file):
        with open(file, "rb") as fh:
            return fh.readline()

    def update_hash(self, file, hash_path):
        with open(hash_path, "wb") as fh:
            fh.write(self.get_hash(file))

    def find_changed(self, path):
        for f in os.listdir(path):
            if f == self.app.CONFIG_FILE:
                continue
            if f == self.app.HASH_DIR:
                continue

            full_path = os.path.normpath(os.path.join(path, f))
            hash_path = self.get_hash_path(full_path)

            if os.path.isfile(full_path):
                if not os.path.isfile(hash_path):
                    if not os.path.isdir(os.path.dirname(hash_path)):
                        os.makedirs(os.path.dirname(hash_path))

                    sys.stdout.write("+ " + full_path + "\n")
                    self.datastore.store(full_path)
                    self.update_hash(full_path, hash_path)

                elif self.get_old_hash(hash_path) != self.get_hash(full_path):
                    sys.stdout.write("+ " + full_path + "\n")
                    self.datastore.store(full_path)
                    self.update_hash(full_path, hash_path)

            else:
                if not os.path.exists(hash_path):
                    sys.stdout.write("+ " + full_path + "/\n")
                    self.datastore.makedirs(full_path)
                    os.makedirs(hash_path)
                self.find_changed(full_path)

    def get_real_path(self, path):
        parts = list(path.split(os.path.sep))
        # remove the Application.HASH_DIR from the path
        while parts[0] == "." or parts[0] == self.app.HASH_DIR:
            parts.pop(0)
        return os.path.normpath("/".join(parts))

    def find_deleted(self, path):
        for f in os.listdir(path):
            hash_path = os.path.join(path, f)
            full_path = self.get_real_path(hash_path)

            if os.path.isfile(hash_path):
                if not os.path.isfile(full_path):
                    sys.stdout.write("x " + full_path + "\n")
                    self.datastore.remove(full_path)
                    os.remove(hash_path)
            else:
                self.find_deleted(hash_path)

    def find_deleted_dirs(self, path):
        for f in os.listdir(path):
            hash_path = os.path.join(path, f)
            full_path = self.get_real_path(hash_path)

            if os.path.isdir(hash_path):
                self.find_deleted_dirs(hash_path)
                if not os.path.exists(full_path):
                    sys.stdout.write("x " + full_path + "/\n")
                    self.datastore.remove_dir(full_path)
                    os.rmdir(hash_path)

    def run(self):
        self.find_changed(".")
        self.find_deleted(self.app.HASH_DIR)
        self.find_deleted_dirs(self.app.HASH_DIR)

    def __init__(self, app):
        self.app = app
        self.datastore = self.app.host.get_data_store()
        self.files = []
        self.upload_files = []
