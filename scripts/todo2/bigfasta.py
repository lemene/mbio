'''从大文件（相对于个人电脑）提取指定名称的read。
'''

import sys
import pickle
import os.path

class BigFasta:
    def __init__(self, filename):
        self.filename = filename
        self.fasta = open(filename, "r")

        self.index = self.load_index()

    def load_index(self):
        index_file = self.filename+".index"

        if os.path.exists(index_file):
            return pickle.load(open(index_file, "rb"))
        else:


            index = {}
            line = self.fasta.readline()
            while line:
                if line[0] == '>':
                    index[line[1:].split()[0]] = self.fasta.tell()
                line = self.fasta.readline()
            pickle.dump(index, open(index_file, "wb"))
            return index

    def get(self, head):
        pos = self.index.get(head, -1)
        if pos >= 0:
            self.fasta.seek(pos)
            return self.load_read()
        else:
            return ""

    def load_read(self):
        seq = []
        for line in self.fasta:
            if line[0] != '>':
                seq.append(line.strip())
            else:
                break
        return "".join(seq)

if __name__ == "__main__":
    bf = BigFasta(sys.argv[1])

    for h in sys.argv[2:]:
        print(r">%s/1/1_0" % h)
        print(bf.get(h))


