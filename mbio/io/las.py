'''读取las文件，daligner生产的比对结果文件或者LAshow输出的文件'''

import re

#  1   1 c   [  687,068..  688,272] x [1,395,267..1,394,063]  ~   0.0%   (4,639,675 x 4,639,675 bps,        0 diffs,     13 trace pts)
#  0   1 2   3  4          5      6   78          9        10     11      12          13                    14           15



class LAshowIter:
    def __init__(self, name):
        self.lashow = open(name)
        self.pattern = re.compile(self.pattern())

    def __iter__(self): return self

    def __next__(self):
        for line in self.lashow:
            if line[0] == '#': continue

            return self.split_line(line)

        raise StopIteration


    def pattern(self):
        number = r" *\d+(,\d+)*"
        p1 = r"(?P<aid>(" + number+ "))" + r"(?P<bid>("+ number + "))" + r" (?P<strand>[n|c]) +"
    
        area = r"([[<])"+number+r"\.\."+number+r"([>\]])"
        areas = area + " x " + area
        p2 = r" +~ +(\d+\.\d)% +"
        lens = r"\(" + number + " x " + number + " bps, +"
        diffs = r"(?P<diffs>("+number+")) diffs, +"
        trace = r"(?P<trace_pts>("+number+")) trace pts\)"
        return "".join([p1, areas, p2, lens, diffs, trace])
    
    def split_line(self, line):

        m = self.pattern.match(line)
        if m != None:
            md = m.groupdict()
            return [int(md["aid"].replace(",","")), int(md["bid"].replace(",","")), md["strand"]]
        else:
            return None

