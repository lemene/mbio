'''读gff文件，官方说明：https://github.com/The-Sequence-Ontology/Specifications/blob/master/gff3.md'''

class GffIter(object):
    def __init__(self, samname):
        self.gff = open(samname)

    def __iter__(self): return self

    def __next__(self):
        for line in self.gff:
            if line[0] == '#' or line.strip() == "" : continue
            seqid, source, type, start, end, score, strand, phase, attributes = line.split()
            return seqid, source, type, int(start), int(end), score, strand, phase, self.split_attr(attributes)

        else:
            raise StopIteration

    @staticmethod
    def split_attr(attr):
        result = {}
        for it in attr.split(";"):
            k, v = it.split("=")
            result[k] = v

        return result

def split_attribute(attr):
    result = {}
    for it in attr.split(";"):
        k, v = it.split("=")
        result[k] = v

    return result

def split_context(line):

    result = {}
    seqid, source, type, start, end, score, strand, phase, attributes = line.split()
    result['seqid'] = seqid
    result['source'] = source
    result['type'] = type
    result['start'] = int(start)
    result['end'] = int(end)
    result['score'] = int(score)
    result['strand'] = strand
    result['phase'] = phase
    result['attributes'] = split_attribute(attributes)

    return result



def print_gff(nfile):
    '''打印gff每行，用于测试'''
    for i in GffIter(nfile):
        print(i)

def summary_methylation(nfile, coverage=25):
    from collections import defaultdict

    rdict = defaultdict(lambda:defaultdict(lambda :{'-':[],'+':[]}))

    for it in GffIter(nfile):
        if int(it[-1]["coverage"]) >= coverage:
            rdict[it[0]][it[2]][it[6]].append(int(it[3]))
    
    return rdict

    #for ref, mdict in rdict.items():
    #    for name, meths in mdict.items():
    #        for strand, pos in meths.items():
    #            print(ref, name, strand, len(pos))

if __name__ == '__main__':
    import sys
    result = locals()[sys.argv[1]](*sys.argv[2:]) 
