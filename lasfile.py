import sys
import struct
import heapq
from dbfile import *

def load_las_file(lasfile):
    with open(lasfile,"rb") as las:
        
        novl = int.from_bytes(las.read(8), byteorder='little')
        tspace = int.from_bytes(las.read(4), byteorder='little')
        print(novl, tspace)

        s = las.read()
        overlaps = []
        off = 0
        for i in range(novl):
            overlaps.append(Overlap()) 
            off += overlaps[-1].unpack(s, off)

        assert len(overlaps) == novl
    return tspace, overlaps


def save_las_file(lasfile, tspace, overlaps):
    with open(lasfile,"wb") as las:
        las.write(struct.pack("q", len(overlaps)))
        las.write(struct.pack("i", tspace))

        for o in overlaps:
            las.write(o.pack())



class ListHeap:
    class Item:

        def __init__(self, l, i):
            (self.l, self.i) = (l, i) 
        def __lt__(self, b):
            return ListHeap.Item.key(self.value()) < ListHeap.Item.key(b.value())

        def value(self): return self.l[self.i]
        def inc(self): self.i += 1
        def end(self): return self.i >= len(self.l) 

    def __init__(self, sorted_lists, key):
        self.lists = sorted_lists
        self.Item.key = key

    def __iter__(self):
        self.heap = [self.Item(l, 0) for l in self.lists if len(l) > 0]
        heapq.heapify(self.heap)        
        return self

    def __next__(self):

        if len(self.heap) > 0:
            r = self.heap[0].value()
            self.heap[0].inc()
            if not self.heap[0].end():
                heapq.heapreplace(self.heap, self.heap[0])
            else:
                heapq.heappop(self.heap)

            return r

        else:
            raise StopIteration 
            
        
class Overlap:
    """对应Daligner的Overlap类型
    flags：& 0x1 是否反向互补
    aread,bread：比较的read的id
    path：参考
    """
    class Path:pass
        
    def __init__(self):
        pass
    
    def unpack(self, s, off):
        align = lambda n: (n+7) // 8 * 8
        
        path = Overlap.Path()
        (b, e) = (0, 4*6)
        (path.tlen, path.diffs, path.abpos, path.bbpos, path.aepos, path.bepos) = struct.unpack("iiiiii", s[off+b:off+e])
        e = align(e)

        (b, e) = (e, e+12)
        (self.flags, self.aread, self.bread) = struct.unpack("iii", s[off+b:off+e])
        e = align(e)

        (b, e) = (e, e + path.tlen)
        path.trace = struct.unpack("{}b".format(path.tlen), s[off+b:off+e])
        self.path = path
        print(path.trace)
        print()
        return e

    def pack(self):
        s = []

        s.append(struct.pack("iiiiii", self.path.tlen, self.path.diffs, self.path.abpos, self.path.bbpos, self.path.aepos, self.path.bepos))
        s.append(struct.pack("iiii", self.flags, self.aread, self.bread, 0))
        s.append(struct.pack("{}b".format(self.path.tlen), *self.path.trace))
        return b"".join(s)


        

def sort_las_file(lasfile, lasSfile):
    (tspace, overlaps) = load_las_file(lasfile)
    ovl_key = lambda x: [x.aread, x.bread, x.flags&0x1, x.path.abpos]
    overlaps.sort(key=ovl_key)
    save_las_file(lasSfile, tspace, overlaps)


def merge_sorted_las_file(lasfile, sored_lasfiles):
    sored_las = [load_las_file(f) for f in sored_lasfiles]

    with open(lasfile, "wb") as las:
        las.write(struct.pack("q", sum([len(e[1]) for e in sored_las])))
        las.write(struct.pack("i", sored_las[0][0]))

        ovl_key = lambda x: [x.aread, x.bread, x.flags&0x1, x.path.abpos]
        for o in ListHeap([e[1] for e in sored_las], ovl_key):
            las.write(o.pack())
   
class LasFile(object):
    def __init__(self, fname, db=None):
        self.fname = fname
        self.db = db
        self.load(fname)

    def load(self, fname):
        self.tspace, self.overlaps = load_las_file(fname)

    def save(self, fname):
        save_las_file(fname, self.tspace, self.overlaps)

    def get(self, i):
        '''获取第i个比对'''
        assert i < self.size()

        o = self.overlaps[i]

        (alen, blen) = (0, 0)
        if self.db != None:
            alen = len(self.db.get(o.aread))
            blen = len(self.db.get(o.bread))
        
        return [o.aread, alen, o.path.abpos, o.path.aepos, o.bread, blen, o.path.bbpos, o.path.bepos]

    def size(self):
        '''比对的个数'''
        return len(self.overlaps)

    def __iter__(self):
        return LasFileIterator(self)

class LasFileIterator(object):
    def __init__(self, lasfile):
        self.lasfile = lasfile
        self.iter = iter(range(self.lasfile.size()))

    def __next__(self):
        return  self.lasfile.get(self.iter.__next__())



if __name__ == "__main__":
    ##merge_sorted_las_file("pt.las", ["raw_reads.raw_reads.N1.las", "raw_reads.raw_reads.N2.las"]);
    load_las_file(r"data/a.b.S.las")

        
