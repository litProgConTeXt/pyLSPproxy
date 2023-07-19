"""
Main entry point for the `lspRecord` tool.

The LSP record tool, works with four distinct channels:

1. The LSP client sends/receives LSP JSON-RPC requests and responses over the
   stdin/stdout of the `lspRecord` tool.

2. The stdout/stdin of the asyncio process running the specified LSP server
   sends/recieves LSP JSON-RPC requests and responses.

3. The JSON-RCP traffic between the LSP client and server are written in NDJson
   format to an csRecord.ndjson file.

4. In order to ensure no spurious logging information get sent over the command
   line's stdout, Logging gets sent to a stanard python logfile.


"""

import aiofiles
import argparse
import asyncio
import json
import sys
import yaml

from pylspproxy.simpleJsonRpc import AsyncJsonRpc, asyncWrapStdinStdout
from pylspproxy.simpleNDJson  import AsyncNDJson
from pylspproxy.communication import client2server, server2client

def parseCli() :
  parser = argparse.ArgumentParser(
    prog="lspRecord",
    description="LSP recording client<->server proxy",
  )
  parser.add_argument('-r', '--record', help="The path to the NDJson record file")
  parser.add_argument('-d', '--debug',  help="The path to the process debugIO file")
  parser.add_argument('command', nargs=argparse.REMAINDER,
    help="All remaining arguments will be treated as a command to be run"
  )
  return vars(parser.parse_args())

async def runRecorder(cliArgs) :
  # connect to the stdio
  clientReader, clientWriter = await asyncWrapStdinStdout()

  # open the debugIO file
  debugIO      = None
  if cliArgs['debug'] :
    debugIO    = await aiofiles.open("/tmp/lspRecord.debugIO", "w")

  # open the ndjson record file
  ndjsonReader = await aiofiles.open('/dev/null',       mode='r')
  ndjsonWriter = await aiofiles.open(cliArgs['record'], mode='w')
  ndJson       = AsyncNDJson(ndjsonReader, ndjsonWriter, debugIO)    

  # start the server
  cmdJson = { "method" : "cmdLine", "params": " ".join(cliArgs['command']) }
  if debugIO :
    await debugIO.write(json.dumps(cmdJson))
    await debugIO.flush()
  await ndJson.record(cmdJson)
  proc = await asyncio.create_subprocess_exec(
    *cliArgs['command'],
    stdin=asyncio.subprocess.PIPE,
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE
  )

  serverReader = proc.stdout
  serverWriter = proc.stdin

  # connect
  c2sRpc = AsyncJsonRpc(clientReader, serverWriter, debugIO)
  s2cRpc = AsyncJsonRpc(serverReader, clientWriter, debugIO)

  # run
  doneEvent = asyncio.Event()

  async with asyncio.TaskGroup() as tg :
    tg.create_task(client2server(doneEvent, c2sRpc, ndJson, proc))
    tg.create_task(server2client(doneEvent, s2cRpc, ndJson, proc))

  await ndjsonReader.close()
  await ndjsonWriter.close()

  if debugIO : await debugIO.close()

  return await proc.wait()

def cli() :
  """
  Main entry point for the `lspRecord` tool.
  """
  cliArgs = parseCli()

  if not cliArgs['record'] :
    print("No record file has been provided...")
    print("... there is nothing to do!")
    sys.exit(-1)

  if not cliArgs['command'] :
    print("No command has been provided...")
    print("... there is nothing to do!")
    sys.exit(-1)

  return asyncio.run(runRecorder(cliArgs))
