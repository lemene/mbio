'''读写fasta文件的工具'''

class Iterator(object):
    '''读取fasta的迭代器，返回head seq'''

    def __init__(self, fname):
        '''
        :param: fastq fasta文件路径
        '''
        self.ifile = open(fname)

    def __iter__(self): return self

    def __next__(self):
        for line in self.ifile:
            if line[0] == '@':
                return (line[1:].split(), self.ifile.readline().strip())

            else:
                pass


        raise StopIteration
