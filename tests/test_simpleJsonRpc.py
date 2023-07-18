"""
Test the AsyncJsonRpc class methods:

- rawReceive
- receive
- sendDict
- sendResult
- sendError
"""


import pytest
import sys
import yaml

from pylspproxy.simpleJsonRpc import AsyncJsonRpc
from tests.utils import ClientServerIO

# NOTE: at the moment IF the AsyncJsonRpc gets out of sync with the JSON-RPC
# message stream, there is NO WAY it can recover.

@pytest.mark.asyncio
async def test_receivePart1() :
  """
  Test that we can use rawReceive to receive a simple message from the "wire"
  """
  cs = ClientServerIO("""Content-Length: 28

{ "msg" : "This is a test" }
""")
  clientJsonRpc = AsyncJsonRpc(cs.reader, cs.writer)
  result = await clientJsonRpc.rawReceive()
  assert isinstance(result, dict)
  assert "msg" in result
  assert result['msg'] == "This is a test"

@pytest.mark.asyncio
async def test_receivePart1_garbledMsg() :
  """
  Test that we can use rawReceive to robustly receive a simple but garbled
  message from the "wire"
  """
  cs = ClientServerIO("""Content-Length: 25

{ "msg" : "This is a test" }
""")
  clientJsonRpc = AsyncJsonRpc(cs.reader, cs.writer)
  result = await clientJsonRpc.rawReceive()
  assert isinstance(result, dict)
  assert "method" in result
  assert result['method'] == "error"
  assert 'params' in result
  assert result['params'].startswith('JSONDecodeError')

@pytest.mark.asyncio
async def test_sendDict() :
  """
  Test that we can send a dict (not necessarily a correct JSON-RPC dict).
  """
  cs = ClientServerIO()
  clientJsonRpc = AsyncJsonRpc(cs.reader, cs.writer)
  await clientJsonRpc.sendDict({
    'msg' : 'This is a test'
  })
  result = cs.writer.getvalue().decode()
  assert result.startswith('Content-Length: 43\r\n\r\n')
  assert -1 < result.find('"msg"')
  assert -1 < result.find('"This is a test"')
  assert -1 < result.find('"jsonrpc"')

@pytest.mark.asyncio
async def test_sendResult() :
  """
  Test that we can send a result message.
  """
  cs = ClientServerIO()
  clientJsonRpc = AsyncJsonRpc(cs.reader, cs.writer)
  await clientJsonRpc.sendResult({
    'msg' : 'This is a test'
  })
  result = cs.writer.getvalue().decode()
  assert result.startswith('Content-Length: 55\r\n\r\n')
  assert -1 < result.find('"result"')
  assert -1 < result.find('"msg"')
  assert -1 < result.find('"This is a test"')
  assert -1 < result.find('"jsonrpc"')

@pytest.mark.asyncio
async def test_sendError() :
  """
  Test that we can send an error message.
  """
  cs = ClientServerIO()
  clientJsonRpc = AsyncJsonRpc(cs.reader, cs.writer)
  await clientJsonRpc.sendError({
    'msg' : 'This is a test'
  })
  result = cs.writer.getvalue().decode()
  assert result.startswith('Content-Length: 54\r\n\r\n')
  assert -1 < result.find('"error"')
  assert -1 < result.find('"msg"')
  assert -1 < result.find('"This is a test"')
  assert -1 < result.find('"jsonrpc"')

@pytest.mark.asyncio
async def test_simple() :
  """
  Test that we can send a dict containing a simple (correctly formated JSON-RPC)
  message.
  """
  cs = ClientServerIO()
  clientJsonRpc = AsyncJsonRpc(cs.reader, cs.writer)
  await clientJsonRpc.sendDict({
    'method' : 'test',
    'params' : "This is a test",
    'id' : 10
  })
  cs.reverse()
  serverJsonRpc = AsyncJsonRpc(cs.reader, cs.writer, sys.stdout)
  methodName, paramsValue, msgId = await serverJsonRpc.receive()
  assert methodName == 'test'
  assert paramsValue == "This is a test"
  assert msgId == 10
  assert len(cs.writer.getvalue().decode()) == 0
  