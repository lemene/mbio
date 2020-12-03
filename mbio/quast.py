from collections import defaultdict

def load_report(fname):
    result = []
    offset = -1
    for line in open(fname):
        if offset == -1:
            if line.startswith("Assembly"):
                its = line.split()
                offset = line.index(its[1])
                assert offset != -1
        else:
            result.append((line[0:offset].strip(), line[offset:].strip()))

    return result

def save_load_report(fname):
    try:
        return load_report(fname)
    except:
        return tuple()

def merge_reports(rps):
    # item order
    item_names = defaultdict(list)
    for rp in rps:
        for i, (k, v) in enumerate(rp):
            item_names[k].append(i)

    item_orders = []
    for k, v in item_names.items():
        item_orders.append([k, sum(v)/len(v)])
    
    item_orders.sort(key=lambda x: x[1]);
    for i, v in enumerate(item_orders):
        v[1] = i

    results = [[i[0] for i in item_orders]]
    for rp in rps:
        r = [None] * len(results[0])
        for k, v in rp:
            r[results[0].index(k)] = v

        results.append(r)

    return results

def merge_report_files(ifnames, ofname, header=[]):
    assert len(header) == 0 or len(header) == len(ifnames)

    results = merge_reports([save_load_report(f) for f in ifnames])
    print(results)

    with open(ofname, "w") as ofile:
        if len(header) > 0: ofile.write(",%s\n" % ",".join(header))

        for i in range(len(results[0])):
            line = [jr[i] if jr[i] != None else "NA" for jr in results]
            ofile.write("%s\n" % ",".join(line))
    


if __name__ == "__main__":
    merge_report_files(["/mnt/e/temp/report0.txt", "dsfa", "/mnt/e/temp/report1.txt"], "a.csv", ["r0", "r1", "r3"])