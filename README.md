Codebase backing xkcdref.info. Companion site for /u/xkcd_transcriber.

Rewritten in flask/gevent.

Includes:

- the webapp

Project uses:

- flask as a web framework
- gevent for concurrency
- sqlite as a datastore
- redis for caching


### Requirements ###
- Python 2.7
- Redis


### Installation ###

```
python setup.py
```