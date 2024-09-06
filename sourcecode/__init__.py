# src/__init__.py

#instead of this:
# from .mi import leiden_clustering, remove_zero_row_col, get_encoded_gene, convert_networkx_to_igraph, calculate_clustering_coefficients, SBM_clustering_coefficients, greedy_modularity_communities, calculate_conductance, centralities, leiden_clustering, get_nodes_df, get_edges_df, SBM_clustering, csvs_more_readable, tag_to_title, heatmap, two_D_network, get_encoded_proteins, process_hits
# from .pca import function2
#
# __all__ = ['function1', 'function2']

# use this:

import os
import pkgutil


package_dir = os.path.dirname(__file__)
for (_, module_name, _) in pkgutil.iter_modules([package_dir]):
    module = __import__(f"{__name__}.{module_name}", fromlist=['*'])

    for k in dir(module):
        if not k.startswith("_"):
            globals()[k] = getattr(module, k)

__all__ = [k for k in globals().keys() if not k.startswith("_")]

# from package import *


