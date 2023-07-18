# LSP proxy

We implement two different commands:

**lspRecord** when used as an LSP (stdio) proxy between an LSP client (VSCode)
and an LSP server (conTeXt-langServer), the `lspRecord` tool will record ALL
JSON-RPC traffic to an NDJson file.

**lspReply** will load a (filtered) NDJson file which records a LSP
client->server session and replays it to the server.

We can use [DbGate](https://dbgate.org/) to browse and filter the ndjson record
file.
