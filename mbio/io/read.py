from . import fasta
from . import fastq

class Iterator(object):
    def __init__(self, fname):
        self.flist = []
        if fname.endswith(".txt"):
            for line in open(fname):
                n = line.strip()
                if len(n) > 0:
                    self.flist.append(n)
        else:
            self.flist.append(fname)

        self.index = 0
        self.iterator = self.__create_iterator(self.flist[0])

    def __create_iterator(self, fname):
        if fname.endswith('.fasta') or fname.endswith(".fasta.gz"):
            print("-", fname)
            return fasta.Iterator(fname)
        elif fname.endswith('.fastq'):
            return fastq.Iterator(fname)
        elif fname.endswith(".txt"):
            return Iterator(fname)
        else:
            return None

    def __iter__(self): return self

    
    def __next__(self):
        while self.index < len(self.flist):
            try:
                return self.iterator.__next__()
            except StopIteration:
                self.index += 1
                if self.index < len(self.flist):
                    self.iterator = self.__create_iterator(self.flist[self.index])
                else:
                    break
            

        raise StopIteration
