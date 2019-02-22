from io import FileIO
import struct
import yaml
import json
import sys

class PacketReader(FileIO):
    _START = 0xAA
    _STOP = 0xCC
    _ESCAPE = 0xBB

    def _skip_to_packet_start(self):
        inchar = ord(self.read(1))
        while inchar != self._START:
            inchar = ord(self.read(1))
        return inchar

    def _parse_input(self, inchar):
        if inchar == self._ESCAPE:
            return ord(self.read(1)) ^ inchar
        else:
            return inchar
        
    def readPacket(self):
        packet = ""
        try:
            inchar = self._skip_to_packet_start()
            while inchar != self._STOP:
                inchar = ord(self.read(1))
                packet += chr(self._parse_input(inchar))
        except:
            return None

        return packet[0:-1]

    def decodeHeader(self, packet):
        res = {}
        (flags, payload_id) = struct.unpack(">BH", packet[0:3])
        res['flags'] = flags
        res['id'] = payload_id
        if flags & 0x4 == 0x4:
          res['seq'] = struct.unpack(">B", packet[3])[0]
        if flags & 0x5 == 0x5:
            res['len'] = struct.unpack(">H", packet[4:6])[0]
        elif flags & 0x1 == 0x1:
            res['len'] = struct.unpack(">H", packet[3:5])[0]

        return res
            
    def packetData(self, packet):
        flags = struct.unpack(">B", packet[0:1])[0]
        start = 3
        if flags & 0x1 == 0x1:
            start += 2
        if flags & 0x4 == 0x4:
            start += 1
        return packet[start:-1]
           
class FieldDecoder():
    def __init__(self, filename):
        self.yml = yaml.load(open('defaultFreeEMSMetaData.yaml','r').read())
        
    def _structName(self, type):
      if type == "UINT8":
        return (1, ">B")
      if type == "UINT16":
        return (2, ">H")
      if type == "SINT8":
        return (1, ">b")
      if type == "SINT16":
        return (2, ">h")
      if type == "BITS8":
        return (1, ">B")
      if type == "BITS16":
        return (2, ">H")

    def decodePacket(self, packet):
        addr = 0
        res = {}
        for field in self.yml['fields']:
            (len, s) = self._structName(field['type'])
            val = struct.unpack(s, packet[addr:addr + len])[0]
            val /= field['divBy']
            addr += len
            res[field['name']] = val
        return res
            

if __name__ == "__main__":
    binfile = sys.argv[1]
    yamlfile = sys.argv[2]
    x = PacketReader(binfile)
    fields = FieldDecoder(yamlfile)

    count = 0
    points = []

    while True:
        y = x.readPacket()
        if y is None:
            break
        if x.decodeHeader(y)['id'] == 401:
            points.append(fields.decodePacket(x.packetData(y)))
        
    print json.dumps(points)
