#!/usr/bin/python

import sys
import urllib

from Alfred import Tools as Tools
import os
import shutil
import MyNotes
import re

def rmDir(path, ignore_errors=True):
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors)
        return not (os.path.exists(path))
    else:
        return False


def rmFile(path):
    path = urllib.url2pathname(path)
    if os.path.isfile(path) and os.path.exists(path):
        os.remove(path)
        return not (os.path.exists(path))
    else:
        return False


def getFileQuery(q):
    return q.split('|') if '|' in q else [q, str()]


def getAssetsLinks(parent_path, p):
    def is_in_notes(f_path):
        return not (str(f_path).startswith('..')) and not (str(f_path).startswith('/'))
    with open(p, 'r') as f:
        content = f.read()
    matches = re.findall(r'\[.*\]\((.*)\)', content)
    return [parent_path + m for m in matches if is_in_notes(m)]


mn = MyNotes.Search()

# Load Env variables
ext = mn.getNotesExtension()
#p = mn.getNotesPath().encode('utf-8')
files_to_delete = sys.argv[1:]

return_text = str()
for query in files_to_delete:
    file_path, last_query = getFileQuery(query)
    if os.path.isfile(file_path) and file_path.endswith(ext):
        file_name = os.path.basename(file_path)


        # Search for links to other assets and delete each file
        parent = mn.getNotesPath()
        assetfile_links = getAssetsLinks(parent, file_path)
        is_assetfile_deleted = False
        for l in assetfile_links:
            # Avoid Markdown file removal
            if not(l.endswith(ext)):
                is_assetfile_deleted = rmFile(l)

        # Delete Assets Folder
        remove_ext = len(ext)
        assets_path = Tools.strJoin(file_path[:-remove_ext], ".assets")
        assets_path_legacy = Tools.strJoin(file_path[:-remove_ext])
        is_asset_deleted = rmDir(assets_path) or rmDir(assets_path_legacy) or is_assetfile_deleted

        # Finally delete the MD File
        is_file_deleted = rmFile(file_path)

        # Create Notification Message
        if len(files_to_delete) == 1:
            return_text = '- MD Note DELETED'if is_file_deleted else "Cannot delete file: %s" % file_name
            return_text += '\n- Assets DELETED' if is_asset_deleted else str()

if len(files_to_delete) > 1:
    return_text = "%s files deleted" % len(files_to_delete)

Tools.notify('MD Note deleted!', return_text)

sys.stdout.write(last_query)
