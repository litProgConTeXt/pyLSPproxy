"""
Test the AsyncNDJson class methods:

- record
- nextRecord

"""

import pytest
import sys
import yaml

from pylspproxy.simpleNDJson import AsyncNDJson
from tests.utils import NDJsonIO

@pytest.mark.asyncio
async def test_nextRecord() :
  """
  Test that we can use nextRecord to read the next record from the NDJson file."
  """
  ndJsonIO = NDJsonIO("""
{ "msg" : "This is a first test" }
    { "msg" : "This is a second test" }     
{    "msg"    :    "This is a third test"    }
{ "msg" : "This is a fourth test" }
""")
  ndJson = AsyncNDJson(ndJsonIO.reader, ndJsonIO.writer, sys.stdout)
  # blank line or corrupted JSON record returns an empty dict
  result = await ndJson.nextRecord()
  assert isinstance(result, dict)
  assert result == {}
  result = await ndJson.nextRecord()
  assert isinstance(result, dict)
  assert "msg" in result
  assert result['msg'] == "This is a first test"
  result = await ndJson.nextRecord()
  assert isinstance(result, dict)
  assert "msg" in result
  assert result['msg'] == "This is a second test"
  result = await ndJson.nextRecord()
  assert isinstance(result, dict)
  assert "msg" in result
  assert result['msg'] == "This is a third test"

@pytest.mark.asyncio
async def test_record() :
  """
  Test that we can use record to write the next record to the NDJson file."
  """
  ndJsonIO = NDJsonIO()
  ndJson = AsyncNDJson(ndJsonIO.reader, ndJsonIO.writer)
  await ndJson.record({"msg" : "This is a first test"})
  assert ndJson.writer.getvalue() == '{"msg": "This is a first test"}\n'
