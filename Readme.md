# python Language Server Protocol Proxy

A simple Python based [Language Server
Protocol](https://microsoft.github.io/language-server-protocol/) [Proxy
](https://en.wikipedia.org/wiki/Proxy_server) which records all traffic to
a [NDJson](http://ndjson.org/) file.

We can use [DbGate](https://dbgate.org/) to browse and filter the ndjson
record file.

## Tools

- [ndjson](https://github.com/rhgrant10/ndjson)

- [Nick Coghlan's TCP echo client/server
  example](https://www.curiousefficiency.org/posts/2015/07/asyncio-tcp-echo-server.html)
  (used under a [CC0
  license](https://creativecommons.org/publicdomain/zero/1.0/))

- [Eli Bendersky's TCP asyncio-echo-server
  example](https://github.com/eliben/python3-samples/blob/master/async/asyncio-echo-server.py)
  (used under the
  [unlicense](https://github.com/eliben/python3-samples/blob/master/LICENSE))

- [Implement a simple echo server using
  asyncio](https://stackoverflow.com/questions/48031844/implement-a-simple-echo-server-using-asyncio)

- [How to create TCP proxy server with
  asyncio?](https://stackoverflow.com/questions/46413879/how-to-create-tcp-proxy-server-with-asyncio)