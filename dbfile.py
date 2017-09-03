"""读取db文件（fasta2DB生成）"""

import os.path
import struct

class Hits:
    class Read:
        fmt = "iii4xqqi4x"
        @staticmethod
        def size():
            return struct.calcsize(Hits.Read.fmt)

        def unpack(self, buf):
            self.origin, self.rlen, self.fpluse, self.boff, self.coff, self.flags = struct.unpack(Hits.Read.fmt, buf)
            return Hits.Read.size()

        def print(self):
            print(self.origin, self.rlen, self.fpluse, self.boff, self.coff, self.flags)

    def __init__(self):
        pass

    def unpack(self, buf):
        (b, e) = (0, struct.calcsize("iiii"))
        (self.ureads, self.treads, self.cutoff, self.all) = struct.unpack("iiii", buf[b:e])

        (b, e) = (e, e+ struct.calcsize("4f"))
        self.freq = struct.unpack("4f", buf[b:e])
        
        (b, e) = (e, e+ struct.calcsize("iq"))
        self.maxlen, self.totlen = struct.unpack("iq", buf[b:e])
        
        (b, e) = (e, e+ struct.calcsize("iiiii"))
        self.nreads, self.trimmed, self.part, self.ufirst, self.tfirst = struct.unpack("iiiii", buf[b:e])
        
        (b, e) = (e, e+ struct.calcsize("PiPPP"))
        self.path, self.loaded, self.bases, self.reads_ptr, self.tracks = struct.unpack("PiPPP", buf[b:e])
        e += 4

        self.reads, off = [], e
        for i in range(self.ureads):
            r = Hits.Read()
            off += r.unpack(buf[off:off+Hits.Read.size()])
            self.reads.append(r)
            #if i > 2: break
    
    def print(self):
        print(self.ureads, self.treads, self.cutoff, self.all)
        print(self.freq)
        print(self.maxlen, self.totlen)
        print(self.nreads, self.trimmed, self.part, self.ufirst, self.tfirst)
        print(self.path, self.loaded, self.bases, self.reads_ptr, self.tracks)

def load_idx_file(idxfile):
    with open(idxfile, "rb") as idx:
        buf = idx.read()
        h = Hits()
        h.unpack(buf)
        h.print()
        return h

def load_bps_file(bpsfile, hits):
    with open(bpsfile, "rb") as bps:
        buf = bps.read()

        

        SEQS = [b'A',b'C',b'G',b'T']
        decomp = lambda x: [SEQS[(x>>(i)) & 0x3] for i in range(6,-1, -2)]

        for r in hits.reads:
            r.seq = [b'N']*r.rlen
            for i in range(r.rlen//4):
                r.seq[4*i:4*i+4] = decomp(buf[r.boff+i])
            else:
                i += 1
                if i*4 < r.rlen:
                    r.seq[i*4:r.rlen] =decomp(buf[r.boff+i])[0:r.rlen-i*4]
            

class DBFile(object):
    def __init__(self, name):

        self.load(name)
    def load(self, name):
        (p, n) = os.path.split(name)
        print(p)
        self.dbname = os.path.join(p, n+".db")
        self.bpsname = os.path.join(p, "."+n+".bps")
        self.idxname = os.path.join(p, "."+n+".idx")

        print(self.idxname)
        self.hits = load_idx_file(self.idxname)
        load_bps_file(self.bpsname, self.hits)


    def get(self, id):
        return self.hits.reads[id].seq
    def save(self, fname):  pass


if __name__ == "__main__":
    db = DBFile("raw_reads")

