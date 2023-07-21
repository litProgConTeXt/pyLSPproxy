"""
Define the asynchornous channel communication between LSP client and server as
well as to/from the NDJson record/replay files.
"""

import logging

from pylspproxy.simpleJsonRpc import AsyncJsonRpc
from pylspproxy.simpleNDJson  import AsyncNDJson

"""
  rpc    = AsyncJsonRpc(pipes.clientReader, pipes.serverWriter)
  ndjson = NDJson(pipes.recordReader, pipes.recordWriter)
"""

async def client2server(done, rpc, ndjson) :
  """ Asynchronously capture all LSP JSON-RPC messages from the client to the
  server. """

  logging.debug("Starting client -> server capture")
  try :
    while not done.is_set() :
      msgDict = await rpc.rawReceive()
      if rpc.reader.at_eof() :
        logging.debug("client2server reader at EOF")
        done.set()
      await ndjson.record(msgDict)
      await rpc.sendDict(msgDict)
  finally : 
    pass
  logging.debug("Finished client -> server capture")

async def server2client(done, rpc, ndjson) :
  """ Asynchronously capture all LSP JSON-RPC messages from the server to the
  client. """

  logging.debug("Starting server -> client capture")
  try :
    while not done.is_set() :
      msgDict = await rpc.rawReceive()
      if rpc.reader.at_eof() :
        logging.debug("server2client reader at EOF")
        done.set()
      if 'jsonrpc' in msgDict :
        await ndjson.record(msgDict)
        await rpc.sendDict(msgDict)
      elif 'params' in msgDict :
        pass
      else :
        logging.debug("server2client received empty message")
        done.set()
  finally :
    pass
  logging.debug("Finished server -> client capture")

async def record2server(done, rpc, ndjsonReplay, ndjsonRecord) :
  """
  Asynchronously capture all LSP JSON-RPC messages from the NDJson record file
  to the server.
  """
  logging.debug("Starting record -> server capture")
  try :
    while not done.is_set() :
      msgDict = await ndjsonReplay.nextRecord()
      if 'jsonrpc' in msgDict :
        await ndjsonRecord.record(msgDict)
        await rpc.sendDict(msgDict)
      elif 'params' in msgDict :
        pass
      else :
        logging.debug("record2server loaded empty message")
        done.set()
  finally :
    pass
  logging.debug("Finished record -> server capture")

async def server2record(done, rpc, ndjson) :
  """
  Asynchronously capture all LSP JSON-RPC messages from the server while sending
  NDJson messages from the record file.
  """

  logging.debug("Starting server -> record capture")
  try :
    while not done.is_set() :
      msgDict = await rpc.rawReceive()
      if rpc.reader.at_eof() :
        logging.debug("server2record reader at EOF")
        done.set()
      await ndjson.record(msgDict)
  finally :
    pass
  logging.debug("Finished server -> record capture")

async def processWatcher(done, proc, taskArray) :

  logging.debug("Starting to monitor server process")
  try : 
    await proc.wait()
    logging.debug("Server process terminated... canceling tasks")
    for aTask in taskArray :
      logging.debug(f"Canceling task: {aTask.get_name()}")
      aTask.cancel("Server process terminated")
  finally : 
    pass
  logging.debug("Finished monitoring server process")