import gzip

class Iterator(object):
    '''读取fasta的迭代器，返回head seq'''

    def __init__(self, fname):
        
        self.fasta = gzip.open(fname, "rt") if fname.endswith(".gz") else open(fname, "r")
        self.head = self.__get_next_head()

    def __iter__(self): return self

    def __next__(self):
        seq = []
        for line in self.fasta:
            if line[0] == '>':
                assert self.head != None

                head_t = self.head
                self.head = line[1:].strip()
                return (head_t, "".join(seq))
            else:
                seq.append(line.strip())

        else:
            if self.head != None:
                head_t = self.head
                self.head = None
                return (head_t, "".join(seq))

        raise StopIteration

    def __get_next_head(self):
        for line in self.fasta:
            if line[0] == '>':
                return line[1:].strip()

        return None
