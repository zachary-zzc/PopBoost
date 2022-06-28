import sys, os
import numpy as np
import argparse
import datetime
from copy import deepcopy

from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Sort Admixture Qmatrix")
    parser.add_argument("-q", "--qmat", dest="qmat", type=str, required=True,
            help="qmatrix folder")
    parser.add_argument("-p", "--pop", dest="pop", type=str, required=True,
            help="population file")
    parser.add_argument("-d", "--dest", dest="dest_dir", type=str, required=True,
            help="output directory")
    parser.add_argument("-o", "--order", dest="order", type=str, default=None,
            help="population order file")
    parser.add_argument("-f", "--fam", dest="fam", type=str, required=False, default=None,
            help="individual fam file")
    parser.add_argument("-k", "--kval", dest="k", type=int, default=-1,
            help="k value for sort population inner individuals, default maximum k")
    parser.add_argument("-s", "--sort", dest="sort", action="store_true", default=False,
            help="sort qmatrix individuals")
    parser.add_argument("-r", "--reps", dest="reps", action="store_true", default=False,
            help="for rep files, each k have multiple experiments")

    args = parser.parse_args()
    return args


def logging(*args):
    print("[{}] ".format(datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S")), *args)


def read_qmatrix(qfile):
    """
    read qmatrix file, return
        k, qmatrix
    """
    with open(qfile) as ifs:
        content = [list(map(float, c.split())) for c in ifs]
    return len(content[0]), np.array(content)


def read_pop(pfile, valid_pops=None):
    """
    read population list file, return
        population list
    """
    with open(pfile) as ifs:
        content = [c.split()[0] for c in ifs]
    if valid_pops is not None:
        content = [c for c in content if c in valid_pops]
    return np.array(content)


class Qmatrix:
    def __init__(self, k, qmat, pops, indvs=None, qfile=None, sort_by_pop=True):
        assert(len(qmat) == len(pops))
        assert(len(qmat[0]) == k)
        if indvs is not None:
            assert(len(indvs) == len(pops))
        self.k = k
        self.qfile = qfile
        # sort qmat by pops, ensure same pop should be adjacent
        if sort_by_pop:
            indices = np.argsort(pops)
            self.pops = pops[indices]
            self.indvs = indvs[indices]
            self.qmat = qmat[indices]
        else:
            self.pops = pops
            self.indvs = indvs
            self.qmat = qmat


    def get_pop_order(self, pop):
        unique = []
        [unique.append(p) for p in self.pops if p not in unique]
        return unique.index(pop)

    def get_pop_by_index(self, index):
        unique = []
        [unique.append(p) for p in self.pops if p not in unique]
        return unique[index]

    def get_pops(self):
        unique = []
        [unique.append(p) for p in self.pops if p not in unique]
        return unique

    def _exch(self, l1, l2):
        order = np.array(range(len(self.pops)))
        order = np.delete(order, l1); order = np.insert(order, l1[0], l2)
        order = np.delete(order, l2); order = np.insert(order, l2[0], l1)
        self.pops = self.pops[order]
        self.qmat = self.qmat[order]
        self.indvs = self.indvs[order]

    def exchange_pop(self, p1, p2):
        p1_indexes = [_[0] for _ in np.argwhere(self.pops == p1)] # population list is a 1D array
        p2_indexes = [_[0] for _ in np.argwhere(self.pops == p2)]
        self._exch(p1_indexes, p2_indexes)

    def reorder(self, plist):
        for index, p in enumerate(plist):
            if index != self.get_pop_order(p):
                self.exchange_pop(p, self.get_pop_by_index(index))

    def exchange_kval(self, k1, k2):
        self.qmat[:, [k1, k2]] = self.qmat[:, [k2, k1]]

    def itercols(self):
        for i in range(self.k):
            yield(self.qmat[:, i])

    def iterpops(self):
        pops = []
        offsets = []
        for index, p in enumerate(self.pops):
            if p in pops:
                continue
            pops.append(p)
            offsets.append(index)
        for i in range(len(pops)):
            if i == len(pops) - 1:
                popmat = self.qmat[offsets[i]: len(self.pops)]
            else:
                popmat = self.qmat[offsets[i]: offsets[i+1]]
            yield(pops[i], offsets[i], popmat)

    def to_file(self, path):
        np.savetxt(path, self.qmat, delimiter=" ", fmt="%f")

    def write_pop(self, path):
        with open(path, "w") as ofs:
            for p in self.pops:
                ofs.write("{}\n".format(p))

    def write_indv(self, path):
        with open(path, "w") as ofs:
            for indv in self.indvs:
                ofs.write("{}\n".format(indv))


def consensus_qmats(qmats):
    k = deepcopy(qmats[0].k)
    pops = deepcopy(qmats[0].pops)
    indvs = deepcopy(qmats[0].indvs)
    avg_qmats = deepcopy(qmats[0].qmat)
    for q in qmats[1:]:
        assert(k == q.k)
        assert((pops == q.pops).all())
        assert((indvs == q.indvs).all())
        avg_qmats += q.qmat
    avg_qmats /= len(qmats)
    return Qmatrix(k, avg_qmats, pops, indvs=indvs, sort_by_pop=False)


def get_dist(a1, a2, method="Euclidean", weights=None, indices=None):
    assert(len(a1) == len(a2))
    if method == "Euclidean":
        return sum([(v1 - v2) ** 2 for v1, v2 in zip(a1, a2)])
    if method == "Weighted_Euclidean":
        if weights is None:
            raise RuntimeError("weights cannot be none for Weighted Euclidean distance")
        assert(len(weights) == len(a1) and len(weights) == len(a2))
        return sum([(v1 - v2) ** 2 * w for w, v1, v2 in zip(weights, a1, a2)])
    if method == "TopN":
        indices = indices if indices is not None else [i for i in range(len(a1))]
        return sum([(v1 - v2) ** 2 for v1, v2 in zip(a1[indices], a2[indices])])
    else:
        raise RuntimeError("Unknown distance method {}".format(method))


def order_kvals(qmats):

    # FIXME: bug in this function, should revise before use it
    """
    input: qmats in dict format, key is the k number, value is the Qmatrix object
           k should be continuous, e.g. from mink=2, maxk=5, then keys should be [2, 3, 4, 5]
    rearange qmats from start k to end k
    """
    mink = min(qmats.keys())
    maxk = max(qmats.keys())
    for k in range(mink, maxk):
        q1 = qmats[k]
        q2 = qmats[k+1]
        order = []
        for index1, col1 in enumerate(q1.itercols()):
            dist = -1
            matching_col = -1
            for index2, col2 in enumerate(q2.itercols()):
                cur_dist = get_dist(col1, col2)
                if dist == -1 or cur_dist < dist:
                    dist = cur_dist
                    matching_col = index2
            order.append(matching_col)
        # if k == 11:
        #     print(order, len(order))
        for i in range(k+1):
            if i not in order:
                order.append(i)
        q2.qmat = q2.qmat[:, order]
    return qmats


def _get_inner_order(q):
    order = []
    for pop in q.iterpops():
        pname, offset, popmat = pop
        # init weights, major components have higher weights
        weights = popmat.sum(axis=0) / len(popmat)
        # get the first individual
        maxval = -1
        first = -1
        for index, arr in enumerate(popmat):
            cur_val = sum([v ** 2 for v in arr])
            if maxval == -1 or cur_val > maxval:
                maxval = cur_val
                first = index
        porder = [first]
        for i in range(len(popmat)-1):
            minval = -1
            curind = -1
            for index, arr in enumerate(popmat):
                if index in porder:
                    continue
                # curval = get_dist(popmat[porder[i]], arr, method="Weighted_Euclidean", weights=weights)
                curval = get_dist(popmat[porder[i]], arr, method="TopN", indices=np.argsort(weights)[-1:][::-1])
                if minval == -1 or curval < minval:
                    minval = curval
                    curind = index
            porder.append(curind)
        porder = [o + offset for o in porder]
        order += porder
    return order


def pop_inner_order(qmats, k):
    """
    input: qmats in dict format, same as function order_kvals
    sort pop individual order by the maxk qmatrix
    """
    mink = min(qmats.keys())
    maxk = max(qmats.keys())
    if k == -1:
        k = maxk
    # sort inner population individuals by the qmatrix with the largest k value
    q = qmats[k]
    order = _get_inner_order(q)
    for k in range(mink, maxk+1):
        qmats[k].qmat = qmats[k].qmat[order]
        qmats[k].indvs = qmats[k].indvs[order]
    return qmats


def xpop_inner_order(qmats_lst, k):
    mink = min(qmats_lst.keys())
    maxk = max(qmats_lst.keys())
    if k == -1:
        k = maxk
    qlst = qmats_lst[k]
    q = consensus_qmats(qlst)
    order = _get_inner_order(q)
    for k in range(mink, maxk+1):
        for q in qmats_lst[k]:
            q.qmat = q.qmat[order]
            q.indvs = q.indvs[order]
    return qmats_lst


def main():
    args = parse_args()
    # read population file
    pops = read_pop(args.pop)
    indvs = None
    if args.fam:
        indvs = read_pop(args.fam)
    logging("Read population file {} done".format(args.pop))
    if args.reps:
        qmats_lst = {}
        for qfile in Path(args.qmat).glob("*.Q"):
            k, mat = read_qmatrix(qfile)
            qmat = Qmatrix(k, mat, pops, indvs=indvs, qfile=qfile)
            if k in qmats_lst:
                qmats_lst[k].append(qmat)
            else:
                qmats_lst[k] = [qmat]
            logging("Read file {} done".format(qfile))
        if args.order:
            pop_order = read_pop(args.order, pops)
            for qlst in qmats_lst.values():
                for qmat in qlst:
                    qmat.reorder(pop_order)
        if args.sort:
            qmats_lst = xpop_inner_order(qmats_lst, args.k)
            logging("Sort Qmatrixes populations inner individual orders... Done")
        for k, qlst in qmats_lst.items():
            for qmat in qlst:
                basename = os.path.basename(qmat.qfile)
                path = os.path.join(args.dest_dir, "sorted.{}".format(basename))
                qmat.to_file(path)
        poppath = os.path.join(args.dest_dir, "pop")
        qmat.write_pop(poppath)
        indvpath = os.path.join(args.dest_dir, "indvs")
        qmat.write_indv(indvpath)
        logging("Write to directory {}".format(args.dest_dir))
    else:
        # init qmats
        qmats = {}
        # read qmat files
        for qfile in Path(args.qmat).glob("*.Q"):
            k, qmat = read_qmatrix(qfile)
            qmats[k] = Qmatrix(k, qmat, pops, indvs=indvs, qfile=qfile)
            logging("Read file {} done".format(qfile))
        if args.order:
            pop_order = read_pop(args.order, pops)
            for qmat in qmats.values():
                qmat.reorder(pop_order)
            logging("Read population order file {} done".format(args.order))
        # qmats = order_kvals(qmats)
        # logging("Sort Qmatrixes columns... Done")
        # print(qmats[12].qmat, len(qmats[12].qmat), len(qmats[12].qmat[0]))
        qmats = pop_inner_order(qmats, args.k)
        logging("Sort Qmatrixes populations inner individual orders... Done")
        for k, qmat in qmats.items():
            path = os.path.join(args.dest_dir, "reorder.{}.Q".format(k))
            qmat.to_file(path)
        poppath = os.path.join(args.dest_dir, "pop")
        qmat.write_pop(poppath)
        indvpath = os.path.join(args.dest_dir, "indvs")
        qmat.write_indv(indvpath)
        logging("Write to directory {}".format(args.dest_dir))

if __name__ == "__main__":
    main()
