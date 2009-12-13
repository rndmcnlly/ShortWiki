ShortWiki
=========
An SMS-based wiki system

Dependencies
------------
Requires a Google Voice account and BeautifulSoup (`easy_install BeautifulSoup`)

How it works
------------
When you run `python shortwiki.py` it will ask you for your Google Account for 
Google Voice. Your Google Voice number is now a wiki service.

Text "HelloWorld Hi! :)" to your number. This writes a wikipage called "HelloWorld".

Now text just "HelloWorld". You should receive "Hi :)" with a footer signature.

You can get a friend to text something like "HelloWorld lolcats!" to edit the page.

Now when you get "HelloWorld", you'll see "lolcats!" by your friend and when.

Make lots of pages! Serve up microcontent over SMS. :)

Authors
-------
Adam Smith <adam@adamsmith.as>
Jeff Lindsay <progrium@gmail.com>

License
-------
MIT