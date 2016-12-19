#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Synchronizing files with ftp server.

Usage:
- To start: python ftpfilesync.py
- To stop: Ctrl + C

Import variable:
- hostname: reomte server ip
- username : user name
- password: user password
- delay: delay time
- toPath: destination path
- fromPath: source path. It will crash if sub-directory is in the path
'''

from ftplib import FTP
from ftplib import error_perm
import threading
import time
import os


class FtpFileSync(threading.Thread):
    """FtpFileSync is a thread that synchronizing files from remote server
    """
    def __init__(self):
        super(FtpFileSync, self).__init__()
        self.hostname = 'localhost'
        self.username = ''
        self.password = ''
        self.kill_received = False
        self.delay = 1
        self.toPath = "C:/test/"
        self.fromPath = "DownLoadPapers/Papers"

        os.chdir(self.toPath)

    def run(self):
        print "String file sync..."
        while not self.kill_received:
            self.sync(self.delay)
        print "Exiting file sync..."

    def sync(self, delay):
        time.sleep(delay)
        print "begin sync"

        # os.listdir returns unicode filename if the directory path is unicode
        # See https://docs.python.org/2/howto/unicode.html
        localFilenames = [x.encode("utf-8") for x in os.listdir(unicode(self.toPath, "utf-8"))]

        ftp = FTP(self.hostname)
        ftp.login(self.username, self.password)
        # it have to be setup for utf-8
        ftp.sendcmd("OPTS utf8 on")
        if self.fromPath:
            ftp.cwd(self.fromPath)
        for filename in ftp.nlst():
            if not self.kill_received:
                # error_perm(code: 550) means the filename could not be found
                # on remote server
                try:
                    if filename not in localFilenames:
                        ftp.retrbinary(
                            "RETR " + filename,
                            open(filename.decode("utf-8"), 'wb').write)
                except error_perm as ex:
                    print ex
                    ftp.close()
                    break
            else:
                print "stop sync"
                ftp.close()
                break
        print "end sync"
        ftp.close()


def main():
    workThread = FtpFileSync()
    workThread.start()

    while workThread.isAlive():
        try:
            time.sleep(2)
        except KeyboardInterrupt:
            print "The processor will stop"
            workThread.kill_received = True
            workThread.join()


if __name__ == '__main__':
    main()
