## Description

Webpush is a simple tool for synchronizing a folder structure with a remote FTP or SFTP server. It's intended audience are web developers who need to push changes from a development system to a server. The ideas this project implements are not new or original; many full featured IDE's geared towards web development provide a similar mechanism for synchronizing changes. The goal is to provide similar functionality to developers using any set of tools for development.

## How it Works

Webpush works by building a tree of hashes that mirrors the folder structure it's being run in. When a new file is encountered, it's uploaded and a hash file is created. As it runs it compares the hash against existing hash files and uploads and updates the hash as necessary. Once it's done uploading new and changed files it goes through the hash directory and finds hashes of files that have been removed, removes them from the remote system and then removes the hash file. The folders and files created by webpush are:

* .webpush/ Contains the hashes of files that have been uploaded to the server.
* .webpush.conf Contains the remote system information.

The .webpush.conf file is created using the --init option. Optionally you can pass the --host option with --sync and skip creating the config file or override its settings.

### Examples

**Initialize SFTP configuration and perform a sync:**

	webpush --init --host sftp://user@server/var/www/somesite
	webpush --sync

**Initialize FTP configuration and perform a sync:**

	webpush --init --host ftp://user:pass@server:port/var/www/somesite
	webpush --sync

**Perform a sync without creating a config file:**

	webpush --sync --host sftp://user@server:port/var/www/somesite

The path part of the URL is an absolute path, meaning the first slash after the host is treated as the root directory, not the directory said user is placed in upon a successful login.

SFTP supports key based authentication. There is currently no support for prompting for a password if none is provided. This feature will come at a later date.

## Notes

This is my first python project. That said, the code probably isn't optimal and further more it probably isn't close to bug free. I've tested against SSH with key based authentication and FTP. I have not tested FTPS however I have written code to support TLS using the builtin FTP support in python.

This project uses the builtin FTP support in python and Paramiko for SSH support.