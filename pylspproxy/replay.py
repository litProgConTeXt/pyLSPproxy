"""
Main entry point for the `lspReplay` tool.

The LSP replay tool, works with two distinct channels:

1. The NDJson file of LSP JSON-RPC resquests and responses.

2. The stdout/stdin of the asyncio process running the specified LSP server
   sends/recieves LSP JSON-RPC requests and responses.

"""

import aiofiles
import argparse
import asyncio
import sys
import yaml

from pylspproxy.simpleJsonRpc import AsyncJsonRpc, asyncWrapStdinStdout
from pylspproxy.simpleNDJson  import AsyncNDJson
from pylspproxy.communication import client2server, server2client

def parseCli() :
  parser = argparse.ArgumentParser(
    prog="lspRecord",
    description="LSP replaying ndjsonReplay<->server proxy",
  )
  parser.add_argument('-R', '--replay', help="The path to the NDJson replay file")
  parser.add_argument('-r', '--record', help="The path to the NDJson record file")
  #parser.add_argument('-l', '--log',    help="The path to the process log file")
  parser.add_argument('command', nargs=argparse.REMAINDER,
    help="All remaining arguments will be treated as a command to be run"
  )
  return vars(parser.parse_args())

async def runReplayer(cliArgs) :
  print(yaml.dump(cliArgs))

  # open the ndjson replay file
  ndjsonReplayReader = await aiofiles.open(cliArgs['replay'], mode='r'),
  ndjsonReplayWriter = await aiofiles.open('/dev/null',       mode='w')

  # open the ndjson record file
  ndjsonRecordReader = await aiofiles.open('/dev/null',       mode='r'),
  ndjsonRecordWriter = await aiofiles.open(cliArgs['record'], mode='w')

  # start the server
  proc = await asyncio.create_subprocess_exec(
    *cliArgs['command'],
    stdin=asyncio.subprocess.PIPE,
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE
  )

  serverReader = proc.stdout
  serverWriter = proc.stdin

  # connect
  r2sRpc = AsyncJsonRpc(serverReader, serverWriter)
  s2rRpc = AsyncJsonRpc(serverReader, serverWriter)
  ndJsonReplay = AsyncNDJson(ndjsonReplayReader, ndjsonReplayWriter)    
  ndJsonRecord = AsyncNDJson(ndjsonRecordReader, ndjsonRecordWriter)    

  # run
  doneEvent = asyncio.Event()

  async with asyncio.TaskGroup() as tg :
    tg.create_task(replay2server(doneEvent, r2sRpc, ndJsonReplay, ndJsonRecord))
    tg.create_task(server2record(doneEvent, s2rRpc, ndJsonReplay, ndJsonRecord))

  await ndjsonReplayReader.close()
  await ndjsonReplayWriter.close()

  await ndjsonReplayReader.close()
  await ndjsonReplayWriter.close()

def cli() :
  """
  Main entry point for the `lspReplay` tool.
  """
  cliArgs = parseCli()

  if not cliArgs['replay'] :
    print("No replay file has been provided...")
    print("... there is nothing to do!")
    sys.exit(-1)

  if not cliArgs['record'] :
    print("No record file has been provided...")
    print("... there is nothing to do!")
    sys.exit(-1)

  if not cliArgs['command'] :
    print("No command has been provided...")
    print("... there is nothing to do!")
    sys.exit(-1)

  asyncio.run(runReplayer(cliArgs))

