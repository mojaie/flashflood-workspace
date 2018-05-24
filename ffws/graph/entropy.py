#
# (C) 2014-2017 Seiji Matsuoka
# Licensed under the MIT License (MIT)
# http://opensource.org/licenses/MIT
#

import math


def entropy(U, N, weight=None):
    """ Returns information entropy of the assignment

    Args:
        U: assignment {class_id: [members,],}
        N: number of objects
        weight: weight factor {object_id: weight},]
    """
    H = 0
    for class_id, members in U.items():
        size = len(members)
        if not size:
            continue
        p = size / N
        if weight is not None:
            w = sum(weight[m] for m in members) / size
        else:
            w = 1
        H -= p * math.log2(p) * w
    return H


def mutual_info_iter(U, V, N, u_weight=None, v_weight=None):
    """ Calculate Mutual information and conditional entropies by each class

    Args:
        U: assignment {class_id: [members,],}
        V: assignment {class_id: [members,],}
        N: number of objects
        u_weight: weight factor {object_id: weight},]
        v_weight: weight factor {object_id: weight},]
    Yields:
        (U, MI, H(U|V), H(V|U)) for each U
    """
    for u, u_members in U.items():
        splogp = 0
        suplogp = 0
        svplogp = 0
        for v, v_members in V.items():
            isec = set(u_members) & set(v_members)
            isize = len(isec)
            if not isize:
                continue
            if u_weight is not None:
                uw = sum(u_weight[i] for i in isec) / isize
            else:
                uw = 1
            if v_weight is not None:
                vw = sum(v_weight[i] for i in isec) / isize
            else:
                vw = 1
            p = isize * N / (len(u_members) * len(v_members))
            splogp += isize / N * math.log2(p) * uw * vw
            suplogp -= isize / N * math.log2(isize / len(v_members)) * uw * vw
            svplogp -= isize / N * math.log2(isize / len(u_members)) * uw * vw
        yield u, splogp, suplogp, svplogp


def performance(C, K, N, c_weight=None, k_weight=None):
    """ Calculate fuzzy NMI and V-measure

    Args:
        C: Truth classes {class_id: [members,],}
        K: Cluster assignment {class_id: [members,],}
    """
    result = {
        "entropy_c": None,
        "entropy_k": None,
        "cond_entropy_ck": None,
        "cond_entropy_kc": None,
        "mi": None,
        "nmi": None,
        "homogeneity": None,
        "completeness": None,
        "v_measure": None
    }
    us, mi, ck, kc = zip(*mutual_info_iter(C, K, N, c_weight, k_weight))
    result["entropy_c"] = ec = entropy(C, N, c_weight)
    result["entropy_k"] = ek = entropy(K, N, k_weight)
    result["cond_entropy_ck"] = eck = sum(list(ck))  # H(U|V)
    result["cond_entropy_kc"] = ekc = sum(list(kc))  # H(V|U)
    result["mi"] = mi = sum(list(mi))  # Mutual information
    result["nmi"] = mi / math.sqrt(ec * ek)  # Normalized mutual information
    result["homogeneity"] = homo = 1 - (eck / ec)  # Homogeneity
    result["completeness"] = comp = 1 - (ekc / ek)  # Completeness
    result["v_measure"] = 2 * homo * comp / (homo + comp)  # V-measure
    return result


def performance_adjusted(stats, logD, ip):
    """ Entropy informations adjusted by chance

    Args:
        stats: entropy_stats results
        logD: log D
        ip: dict of interpolation functions (scipy.interpolate)
    """
    result = {}
    for stat, func in ip.items():
        exp = float(ip[stat](logD))
        key = "adj_{}".format(stat)
        if exp != 1:
            result[key] = (stats[stat] - exp) / (1 - exp)
        else:
            result[key] = None
    return result
