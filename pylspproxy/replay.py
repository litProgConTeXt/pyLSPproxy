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
import json
import sys
import yaml

from pylspproxy.simpleJsonRpc import AsyncJsonRpc, asyncWrapStdinStdout
from pylspproxy.simpleNDJson  import AsyncNDJson
from pylspproxy.communication import record2server, server2record

def parseCli() :
  parser = argparse.ArgumentParser(
    prog="lspRecord",
    description="LSP replaying ndjsonReplay<->server proxy",
  )
  parser.add_argument('-R', '--replay', help="The path to the NDJson replay file")
  parser.add_argument('-r', '--record', help="The path to the NDJson record file")
  parser.add_argument('-d', '--debug', help="The path to the process debugIO file")
  parser.add_argument('command', nargs=argparse.REMAINDER,
    help="All remaining arguments will be treated as a command to be run"
  )
  return vars(parser.parse_args())

async def runReplayer(cliArgs) :
  # open the debugIO file
  debugIO      = None
  if cliArgs['debug'] :
    debugIO    = await aiofiles.open("/tmp/lspRecord.debugIO", "w")

  # open the ndjson replay file
  ndjsonReplayReader = await aiofiles.open(cliArgs['replay'], mode='r')
  ndjsonReplayWriter = await aiofiles.open('/dev/null',       mode='w')
  ndJsonReplay = AsyncNDJson(ndjsonReplayReader, ndjsonReplayWriter, debugIO)

  # open the ndjson record file
  ndjsonRecordReader = await aiofiles.open('/dev/null',       mode='r')
  ndjsonRecordWriter = await aiofiles.open(cliArgs['record'], mode='w')
  ndJsonRecord = AsyncNDJson(ndjsonRecordReader, ndjsonRecordWriter, debugIO)

  # start the server
  cmdJson = { "method": "cmdLine", "params": " ".join(cliArgs['command']) }
  if debugIO :
    await debugIO.write(json.dumps(cmdJson))
    await debugIO.flush()
  await ndJsonRecord.record(cmdJson)
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

  # run
  doneEvent = asyncio.Event()

  async with asyncio.TaskGroup() as tg :
    tg.create_task(record2server(doneEvent, r2sRpc, ndJsonReplay, ndJsonRecord, proc))
    tg.create_task(server2record(doneEvent, s2rRpc, ndJsonRecord, proc))

  await ndjsonReplayReader.close()
  await ndjsonReplayWriter.close()

  await ndjsonReplayReader.close()
  await ndjsonReplayWriter.close()

  if debugIO : await debugIO.close()

  return await proc.wait()

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

  return asyncio.run(runReplayer(cliArgs))

