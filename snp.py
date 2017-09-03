'''寻找reads的SNP'''

import re


def find_snp(one_blasr_result, refseq, snps):        
    (QNAME, FLAG, RNAME, POS, CIGAR, SEQ) = (l[0], int(l[1]), l[2], int(l[3])-1, l[5], l[9])




cigar_re = r"(\d+)([MIDNSHP=X])"

def find_single_modified_snp_from_blasr(blasr_result, refseq):
    '''从blasr的比较结果中找出只修改了一个的snp，该方法参考falcon_unzip的phasing过程。
    reads和reference比较，
    '''

    snps =  [[[], [], [], []] for c in refseq]

    with open(blasr_result, "r") as f:
        for line in f:
            



def read_ref():
    with open("contig.fasta", "r") as f:
        for line in f:
            if line[0] != ">":
                return line.strip()

    return None

def make_het_call():

    bam_fn = "000.sorted"
    ctg_id = "utg000001l"
    ref_seq = read_ref()
    base_dir = "."
    samtools = "samtools"
    vmap_fn = "vmap_file"
    vpos_fn = "vpos_file"
    q_id_map_fn = "q_id_map_file"


    # maybe we should check if the samtools path is valid
    p = subprocess.Popen(shlex.split("%s view %s %s" % (samtools, bam_fn, ctg_id) ), stdout=subprocess.PIPE)
    pileup = {}
    q_id_map = {}
    q_max_id = 0
    q_id = 0
    q_name_to_id = {}

    try:
        os.makedirs("%s/%s" % (base_dir, ctg_id))
    except OSError:
        pass

    vmap = open(vmap_fn, "w")
    vpos = open(vpos_fn, "w")
    
    VMAP = ['A', 'C', 'G', 'T']
    MAP = {'A':0, 'C':1, 'G':2, 'T':3}
    pipeup = [[list(), list(), list(), list()] for c in ref_seq]


    for l in p.stdout:
        l = l.decode().strip().split()
        if l[0][0] == "@":
            continue

        (QNAME, FLAG, RNAME, POS, CIGAR, SEQ) = (l[0], int(l[1]), l[2], int(l[3])-1, l[5], l[9])

        if QNAME not in q_name_to_id:
            q_id = q_max_id
            q_name_to_id[QNAME] = q_id
            q_max_id += 1

        q_id = q_name_to_id[QNAME]
        q_id_map[q_id] = QNAME
        rp = POS
        qp = 0

        skip_base = 0
        total_aln_pos = 0
        for m in re.finditer(cigar_re, CIGAR):
            adv = int(m.group(1))
            total_aln_pos += adv

            if m.group(2)  == "S":
                skip_base += adv

        if total_aln_pos < 2000 or 1.0 - 1.0 * skip_base / total_aln_pos < 0.1:
            continue
        
        for m in re.finditer(cigar_re, CIGAR):
            adv = int(m.group(1))

            if m.group(2) in ("M", "=", "X"):
                for i in range(adv):
                    pipeup[rp+i][MAP[SEQ[qp+i]]].append(q_id)
                rp += adv
                qp += adv
            elif m.group(2) in ("S", "I"):
                qp += adv
            elif m.group(2) == "D":
                rp += adv

            
  
    print("--------")
    th = 0.25
    for pos, qids in enumerate(pipeup):

        count = [len(ids)  for ids in qids]
        total = sum(count)

        if total > 10:
            percent = [c / total for c in count]
            index = sorted(range(len(percent)), key=percent.__getitem__)

            if 1 - th > percent[index[-1]] and percent[index[-2]] > th:
                print(pos+1, ref_seq[pos], total, " ".join(["%s %d" % (e, c) for e, c in zip(VMAP, count)]), file=vpos)
            
                for qid in qids[index[-1]]:
                    print(pos+1, ref_seq[pos], VMAP[index[-1]], qid, file=vmap)
                for qid in qids[index[-2]]:
                    print(pos+1, ref_seq[pos], VMAP[index[-2]], qid, file=vmap)

    
    print("--------")


    q_id_map_f = open(q_id_map_fn, "w")
    for q_id, q_name in list(q_id_map.items()):
        print(q_id, q_name, file=q_id_map_f)


if __name__ == "__main__":
    make_het_call()

