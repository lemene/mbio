'''
名词解释：
    block: 一段contig上的snp信息
    fragment: read上的snp信息
    pair: haplotype pair，一种
    partition: 指fragment的一种分割，同一分组的fragment所属的染色体相同

'''
import numpy as np

def str_to_num(s):
    '''将字符串数据转换成数值数据'''
    s_to_n = {'0':1, '1':-1, '-':0}
    return np.array([s_to_n[i] for i in s], dtype=np.int8)
    
def num_to_str(n):
    n_to_s = '1-0'
    return "".join([n_to_s[i+1] for i in n])

def overlap(offset1, size1, offset2, size2):
    if offset1+size1 > offset2 and offset2+size2 > offset1:
        
        start1, start2 = (0, offset1-offset2) if offset1>=offset2 else (offset2-offset1, 0)
        size = min(offset1+size1, offset2+size2) - max(offset1, offset2)
        return (True, (start1, start2, size))
    else:
        return (False, None)

class Fragment:
    def __init__(self, id, offset, value):
        '''
        Parameters
        ==========
            id: Fragment的id
            offset: Fragment相对block的偏移量
            value: fragment在对应snp为位置的值，
        '''
        self.id, self.offset = id, offset
        if type(value) == str:
            self.value = str_to_num(value)
        elif type(value) == np.ndarray:
            self.value = value
        elif type(value) == list and type(value[0]) == int:
            self.value = np.array(value, dtype=int)
        elif type(value) == list and type(value[0]) == str:
            self.value = str_to_num(value)
        else:
            print(type(value))

    def fragment_cut(self, frag):
        ol = overlap(self.offset, len(self.value), frag.offset, len(frag.value))
        if ol[0]:
            return (self.value[ol[1][0]:ol[1][0]+ol[1][2]]*frag.value[ol[1][1]:ol[1][1]+ol[1][2]]).sum()*-1
        else:
            return 0    

    def _error_correction(self, pair, offset):
        ol = overlap(self.offset, len(self.value), offset, len(pair))
        if ol[0]:
            s0, s1, e0, e1 = ol[1][0], ol[1][1], ol[1][0]+ol[1][2], ol[1][1]+ol[1][2]
            return True, (sum(self.value[s0:e0]*pair[s1:e1] == -1), sum(self.value[s0:e0]*pair[s1:e1]*-1 == -1))
        else:
            return False, (0, 0)

    def error_correction(self, pair, offset=0):
        _, ec = self._error_correction(pair, offset)
        return min(ec)

    def partition(self, pair, offset=0):
        overlap, ec = self._error_correction(pair, offset)
        if ec[0] > ec[1]:
            return 1
        elif ec[0] < ec[1]:
            return 0
        else:
            return -1

class Block:
    def __init__(self):
        self.frags = []
        self.vindex = {}
        self.findex = {}
        self.variants = None
    
    def add_variants(self, variants):
        self.vindex = { v:i for i, v in enumerate(variants[0]) }
        self.variants = variants[1]

    def add_fragments(self, fragments):
        '''fragments [(id, [(pos, v)])]'''
        for f in fragments:
            sorted_f = sorted(f[1], key=lambda x: self.vindex[x[0]])
            start, end = self.vindex[sorted_f[0][0]], self.vindex[sorted_f[-1][0]]
            value = np.zeros(end-start+1,dtype=np.int8)
            for sf in sorted_f:
                value[self.vindex[sf[0]] - start] = 1 if sf[1] == 0 else -1

            self.frags.append(Fragment(f[0], start, value))
        
        self.frags.sort(key=lambda x: (x.offset, x.offset+len(x.value)))

        for i, f in enumerate(self.frags):
            self.findex[f.id] = i
        
    def add_fragment(self, rid, values):
        self.frags[rid] = values

    def add_variant(self, pos, bp0, bp1):
        self.variants[pos] = (bp0, bp1)

    def size(self):
        return (len(self.findex), len(self.vindex))
     
    def get_fragment(self, rid):
        return self.frags[self.findex[rid]]
    
    def get_error_correction(self, pair, offset=0):
        '''h表示'''
        pair = str_to_num(pair)

        ec = 0
        for f in self.frags:
            ec += f.error_correction(pair, offset)
        return ec

    def get_variants_string_value(self, h):
        prev = self.vindex[h[0][0]]
        v = ['0' if self.variants[prev][0] == h[0][1] else '1']
        for i in h[1:]:
            curr = self.vindex[i[0]]
            if curr > prev + 1: v.append('-'*(curr-prev-1))
            v.append('0' if self.variants[curr][0] == i[1] else '1')
            prev = curr
            
        return self.vindex[h[0][0]], "".join(v)
        

    def get_fragment_cut(self, partition):
        import itertools
        fc = 0
        for i, j in itertools.product(partition[0], partition[1]):
            fc += self.frags[self.findex[i]].fragment_cut(self.frags[self.findex[j]])
        return fc
                
    def pair_to_partition(self, pair, offset=0):
        '''haplotype pair 转换成 partition'''

        partition = [[], []]
        for f in self.frags:
            p = f.partition(pair, offset)
            if p >= 0:
                partition[p].append(f.id)
        return partition

    def partition_to_pair(self, partition):
        '''将partition 转换成 haplotype pair'''
        pass


    
M = np.array([
    [0,1,1],
    [1,1,0]])

H = np.array([
    [1,-1, -1],
    [-1,1,1]])


