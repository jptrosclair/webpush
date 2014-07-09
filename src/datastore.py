import sys

class DataStore:
    @property
    def terminal_size(self):
        import fcntl, termios, struct
        h, w, hp, wp = struct.unpack('HHHH', fcntl.ioctl(0, termios.TIOCGWINSZ, struct.pack('HHHH', 0, 0, 0, 0)))
        return w, h

    def clear_line(self):
        w, h = self.terminal_size
        sys.stdout.write("\r{0}\r".format(" ".ljust(w - 1)))

    def format_bytes(self, bytes):
        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        size = float(bytes)
        count = 0

        while size > 1024:
            size /= 1024
            count += 1

            if count >= len(units) - 1:
                break

        return "{0:.2f} {1}".format(round(size, 2), units[count])

    def progress(self, received, total):
        if received == total:
            self.clear_line()
        else:
            perc = 0
            if received > 0 and total > 0:
                perc = float(received) / float(total)
            self.clear_line()
            sys.stdout.write("\r{0}/{1} {2:.2%}".format(self.format_bytes(received), self.format_bytes(total), perc))
        sys.stdout.flush()

    def remove(self, file):
        pass

    def store(self, file):
        pass

    def remove_dir(self, dir):
        pass

    def make_dir(self, dir):
        pass

    def __init__(self, synchost):
        self.synchost = synchost
        print "Connecting to " + self.synchost.host + ":" + str(self.synchost.port) + \
              "/" + self.synchost.scheme
        print "Syncing to " + self.synchost.path