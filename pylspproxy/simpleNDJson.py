"""
A simple AsyncNDJson library.
"""

import json

class AsyncNDJson :
  """
  An AsyncNDJson class to manage reading and writing AsyncNDJson records to/from a file in
  the file-system.
  """

  def __init__(self, reader, writer, debugIO=None) :
    """
    Initialize an AsyncNDJson object with its associated reader, writer and
    (optional) debug streams.
    """
    self.reader = reader
    self.writer = writer
    self.debugIO = debugIO

  async def record(self, aMsgDict) :
    """
    Record the msgDict as a JSON value on a single line.
    """
    jsonStr = json.dumps(aMsgDict) + "\n"
    await self.writer.write(jsonStr)

  async def nextRecord(self) :
    """
    Read the next line containing a JSON value.

    If the line is empty or the JSON value is corrupted, returns the empty dict.
    """

    aLine = await self.reader.readline()
    if self.debugIO :
      self.debugIO.write(f"[{aLine}]")
      self.debugIO.flush()
    jsonDict = {}
    try :
      jsonDict = json.loads(aLine)
    except: 
      pass
    return jsonDict 
