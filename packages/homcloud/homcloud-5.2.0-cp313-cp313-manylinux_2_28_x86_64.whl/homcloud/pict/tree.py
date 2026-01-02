import homcloud.pict_tree as ext
from homcloud.pdgm_format import PDGMWriter, PDChunk


def save_pdgm(f, dim, sign_flipped, lower_mergetree, upper_mergetree):
    writer = PDGMWriter(f, "bitmap-tree", dim)
    writer.sign_flipped = sign_flipped
    writer.append_chunk(pdchunk(lower_mergetree))
    writer.append_chunk(pdchunk(upper_mergetree))
    writer.append_simple_chunk("bitmap_phtrees", merge_tree_to_dict(lower_mergetree), degree=0)
    writer.append_simple_chunk("bitmap_phtrees", merge_tree_to_dict(upper_mergetree), degree=dim - 1)
    writer.write()


def pdchunk(mt):
    return PDChunk("pd", mt.degree(), *tree_to_pd(mt))


def tree_to_pd(mergetree):
    births = []
    deaths = []
    ess_births = []
    for n in range(mergetree.num_nodes()):
        if mergetree.node_is_trivial(n):
            continue
        if mergetree.node_birth_time(n) == mergetree.node_death_time(n):
            continue
        if mergetree.node_is_essential(n):
            ess_births.append(mergetree.node_birth_time(n))
        else:
            births.append(mergetree.node_birth_time(n))
            deaths.append(mergetree.node_death_time(n))
    return births, deaths, ess_births


def merge_tree_to_dict(mt):
    return {
        "degree": mt.degree(),
        "nodes": {
            mt.node_id(n): {
                "id": mt.node_id(n),
                "birth-time": mt.node_birth_time(n),
                "death-time": mt.node_death_time(n),
                "birth-pixel": mt.node_birth_pixel(n),
                "death-pixel": mt.node_death_pixel(n),
                "volume": mt.node_volume(n),
                "parent": mt.node_parent(n),
                "children": mt.node_children(n),
            }
            for n in range(mt.num_nodes())
            if not mt.node_is_on_boundary(n)
        },
    }


def construct_mergetrees(array, is_superlevel):
    mergetree_lower = ext.MergeTree(array.astype(float), is_superlevel, True)
    mergetree_lower.compute()
    mergetree_upper = ext.MergeTree(array.astype(float), is_superlevel, False)
    mergetree_upper.compute()
    return mergetree_lower, mergetree_upper


def construct_dict(dim, sign_flipped, lower_mergetree, upper_mergetree):
    return {
        "dim": dim,
        "sign-flipped": sign_flipped,
        "lower": merge_tree_to_dict(lower_mergetree),
        "upper": merge_tree_to_dict(upper_mergetree),
    }
