#!/usr/bin/python

from __future__ import with_statement
from googlevoice import Voice
import sys, time
import BeautifulSoup
import urllib
import simplejson
import time

voice = Voice()

WIKI_FILE = 'wiki.json'

# by John Nagle
#   nagle@animats.com
def extractsms(htmlsms) :
    msgitems = []
    tree = BeautifulSoup.BeautifulSoup(htmlsms)	
    conversations = tree.findAll("div",attrs={"id" : True},recursive=False)
    for conversation in conversations:
        rows = conversation.findAll(attrs={"class" : "gc-message-sms-row"})
        for row in rows:
            msgitem = {"id" : conversation["id"]}
            spans = row.findAll("span",attrs={"class" : True}, recursive=False)
            for span in spans:
                cl = span["class"].replace('gc-message-sms-', '')
                msgitem[cl] = (" ".join(span.findAll(text=True))).strip()
            msgitems.append(msgitem)
    return msgitems


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
    requests = []
    
    voice.sms()
    msg_body = {}
    msg_meta = [m for m in voice.sms().messages if not m.isRead]
    for m in extractsms(voice.sms.html):
        msg_body[m['id']] = m
    for m in msg_meta:
        if m.id in msg_body:
            msg = dict(m)
            msg.update(msg_body[m.id])
            requests.append(dict(
                src=msg['phoneNumber'], 
                txt=msg['text'], 
                t=int(time.mktime(msg['startTime']))-28800))
            m.delete()
            
    return requests

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
    print "Write on page '%s' from %s." % (page, src)

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
        print "Read on page '%s' from %s." % (txt, src)
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
    voice.send_sms(dst, payload)

def main(args):

    voice.login()

    init_wiki()

    wiki = load_wiki()

    print "Running..."
    while True:
        requests = get_requests()
        if len(requests):
            print "Got %s requests." % len(requests)
        reads, writes = moses(requests)

        # process writes before reads so readers get the latest data
        for write in writes:
            do_write(write, wiki)
            
        dump_wiki(wiki)

        for read in reads:
            do_read(read, wiki)

        time.sleep(3)

if __name__ == '__main__':
    import sys
    main(sys.argv)
