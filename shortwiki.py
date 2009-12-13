#!/usr/bin/python

from __future__ import with_statement
import urllib
import simplejson
import time

WIKI_FILE = 'wiki.json'

def init_wiki():
    import os
    if not os.path.exists(WIKI_FILE):
        wiki = {}
        dump_wiki(wiki)

def load_wiki():
    with open(WIKI_FILE, 'r') as f:
        wiki = simplejson.load(f)
    return wiki

def dump_wiki(wiki):
    with open(WIKI_FILE, 'w') as f:
        simplejson.dump(wiki, f)
        f.write("\n")

def get_requests():
    u = urllib.urlopen('http://localhost/~adam/incoming.json')
    json = u.read()
    u.close()
    return simplejson.loads(json)

def moses(requests):
    reads = [r for r in requests if r['txt'].find(' ') == -1]
    writes = [r for r in requests if r['txt'].find(' ') != -1]
    return reads, writes

def do_write(write, wiki):
    src = write['src']
    t = write['t']
    txt = write['txt']

    idx = txt.find(' ')
    page = txt[:idx]
    content = txt[idx+1:]
    wiki[page] = {
        'page': page,
        'content': content,
        'author': src,
        'mtime': int(t)}

def do_read(read, wiki):
    src = read['src']
    t = read['t']
    txt = read['txt']
    page = txt

    if txt in wiki:
        entry = wiki[page]
        content = entry['content']
        delay = int(time.time()) - entry['mtime']
        author = entry['author']
        send_response(src, "%s %s/%s" % (content, author, delay_gist(delay)))
    else:
        send_response(src, '~')

def delay_gist(seconds):
    if seconds < 60:
        return "%ds" % int(seconds)
    if seconds < 3600:
        return "%dm" % int(seconds/60)
    if seconds < 86400:
        return "%dh" % int(seconds/3600)
    if seconds < 2629743.83:
        return "%dd" % int(seconds/86400)
    if seconds < 31556929:
        return "%dmo" % int(seconds/2629743.83)
    else:
        return "%dyr" % int(seconds/31556929)

def send_response(dst, payload):
    print "SEND_SMS(%s)" % dst, payload

def main(args):

    init_wiki()

    wiki = load_wiki()

    while True:
        print 'fetching new requests...'

        requests = get_requests()
        reads, writes = moses(requests)


        # process writes before reads so readers get the latest data
        for write in writes:
            do_write(write, wiki)
            
        dump_wiki(wiki)

        for read in reads:
            do_read(read, wiki)

        delay = 5
        print 'sleeping:', delay
        time.sleep(delay)

if __name__ == '__main__':
    import sys
    main(sys.argv)
