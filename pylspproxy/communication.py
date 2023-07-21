"""
Define the asynchornous channel communication between LSP client and server as
well as to/from the NDJson record/replay files.
"""


from pylspproxy.simpleJsonRpc import AsyncJsonRpc
from pylspproxy.simpleNDJson  import AsyncNDJson

"""
  rpc    = AsyncJsonRpc(pipes.clientReader, pipes.serverWriter)
  ndjson = NDJson(pipes.recordReader, pipes.recordWriter)
"""

async def client2server(done, rpc, ndjson, proc) :
  """ Asynchronously capture all LSP JSON-RPC messages from the client to the
  server. """

  try :
    while not done.is_set() :
      msgDict = await rpc.rawReceive()
      if rpc.reader.at_eof() : done.set()
      if proc.returncode is not None : done.set()
      await ndjson.record(msgDict)
      await rpc.sendDict(msgDict)
  finally : 
    pass

async def server2client(done, rpc, ndjson, proc) :
  """ Asynchronously capture all LSP JSON-RPC messages from the server to the
  client. """

  try :
    while not done.is_set() :
      msgDict = await rpc.rawReceive()
      if rpc.reader.at_eof() : done.set()
      if proc.returncode is not None : done.set()
      if 'jsonrpc' in msgDict :
        await ndjson.record(msgDict)
        await rpc.sendDict(msgDict)
      elif 'params' in msgDict :
        pass
      else :
        done.set()
  finally :
    pass

async def record2server(done, rpc, ndjsonReplay, ndjsonRecord, proc) :
  """
  Asynchronously capture all LSP JSON-RPC messages from the NDJson record file
  to the server.
  """

  try :
    while not done.is_set() :
      msgDict = await ndjsonReplay.nextRecord()
      if proc.returncode is not None : done.set()
      if 'jsonrpc' in msgDict :
        await ndjsonRecord.record(msgDict)
        await rpc.sendDict(msgDict)
      elif 'params' in msgDict :
        pass
      else :
        done.set()
  finally :
    pass

async def server2record(done, rpc, ndjson, proc) :
  """
  Asynchronously capture all LSP JSON-RPC messages from the server while sending
  NDJson messages from the record file.
  """

  try :
    while not done.is_set() :
      msgDict = await rpc.rawReceive()
      if rpc.reader.at_eof() : done.set()
      if proc.returncode is not None : done.set()
      await ndjson.record(msgDict)
  finally :
    pass

async def processWatcher(done, proc, taskArray) :

  try : 
    await proc.wait()
    for aTask in taskArray :
      aTask.cancel("Server process terminated")
  finally : 
    pass