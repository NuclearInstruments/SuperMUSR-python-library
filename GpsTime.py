# automatically generated by the FlatBuffers compiler, do not modify

# namespace: 

import flatbuffers
from flatbuffers.compat import import_numpy
np = import_numpy()

class GpsTime(object):
    __slots__ = ['_tab']

    @classmethod
    def SizeOf(cls):
        return 14

    # GpsTime
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # GpsTime
    def Year(self): return self._tab.Get(flatbuffers.number_types.Uint8Flags, self._tab.Pos + flatbuffers.number_types.UOffsetTFlags.py_type(0))
    # GpsTime
    def Day(self): return self._tab.Get(flatbuffers.number_types.Uint16Flags, self._tab.Pos + flatbuffers.number_types.UOffsetTFlags.py_type(2))
    # GpsTime
    def Hour(self): return self._tab.Get(flatbuffers.number_types.Uint8Flags, self._tab.Pos + flatbuffers.number_types.UOffsetTFlags.py_type(4))
    # GpsTime
    def Minute(self): return self._tab.Get(flatbuffers.number_types.Uint8Flags, self._tab.Pos + flatbuffers.number_types.UOffsetTFlags.py_type(5))
    # GpsTime
    def Second(self): return self._tab.Get(flatbuffers.number_types.Uint8Flags, self._tab.Pos + flatbuffers.number_types.UOffsetTFlags.py_type(6))
    # GpsTime
    def Millisecond(self): return self._tab.Get(flatbuffers.number_types.Uint16Flags, self._tab.Pos + flatbuffers.number_types.UOffsetTFlags.py_type(8))
    # GpsTime
    def Microsecond(self): return self._tab.Get(flatbuffers.number_types.Uint16Flags, self._tab.Pos + flatbuffers.number_types.UOffsetTFlags.py_type(10))
    # GpsTime
    def Nanosecond(self): return self._tab.Get(flatbuffers.number_types.Uint16Flags, self._tab.Pos + flatbuffers.number_types.UOffsetTFlags.py_type(12))

def CreateGpsTime(builder, year, day, hour, minute, second, millisecond, microsecond, nanosecond):
    builder.Prep(2, 14)
    builder.PrependUint16(nanosecond)
    builder.PrependUint16(microsecond)
    builder.PrependUint16(millisecond)
    builder.Pad(1)
    builder.PrependUint8(second)
    builder.PrependUint8(minute)
    builder.PrependUint8(hour)
    builder.PrependUint16(day)
    builder.Pad(1)
    builder.PrependUint8(year)
    return builder.Offset()
