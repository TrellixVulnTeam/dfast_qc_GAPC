import os
from ete3 import NCBITaxa
from .config import config
from .common import get_logger

logger = get_logger(__name__)


ete3_db_file = os.path.join(config.DQC_REFERENCE_DIR, config.ETE3_SQLITE_DB)
# if not os.path.exists(ete3_db_file):
#     open(ete3_db_file, "w")  # create an empty file if not exists

ncbi_taxonomy = NCBITaxa(dbfile=ete3_db_file)

def is_prokaryote(taxid):
    lineage = ncbi_taxonomy.get_lineage(taxid)
    return 2 in lineage or 2157 in lineage  # 2: Bacteria, 2157: Archaea

def get_rank(taxid):
    rank_dict = ncbi_taxonomy.get_rank([taxid])
    rank = rank_dict.get(taxid, "")
    if rank == "superkingdom":
        rank = "domain"  # for Bacteria, Archaea
    return rank

def get_taxid(taxon_name, rank):
    taxid_dict = ncbi_taxonomy.get_name_translator([taxon_name])

    taxid_candidates = taxid_dict.get(taxon_name, [])
    taxid_candidates = [taxid for taxid in taxid_candidates if is_prokaryote(taxid)]
    taxid_candidates = [taxid for taxid in taxid_candidates if get_rank(taxid)==rank]
    if len(taxid_candidates) > 1:
        logger.warning("Cannot determine taxid for '%s (%s)'. %s", taxon_name, rank, str(taxid_candidates))
        return None
    elif len(taxid_candidates) == 0:
        logger.warning("Cannot find taxid for '%s (%s)'.", taxon_name, rank)
        return None
    else:
        return taxid_candidates[0]

def get_ascendants(taxid):
    lineage = ncbi_taxonomy.get_lineage(taxid)
    if lineage is None:
        return [0]
    return reversed(lineage)

def get_names(taxid_list):  # only used for debugging
    if len(taxid_list) == 1 and taxid_list[0] == 0:
        return ["Prokaryote"]  # taxid 0 for Prokaryote 
    names = ncbi_taxonomy.get_taxid_translator(taxid_list)
    taxon_names = [f"{taxid}:{names[taxid]}" for taxid in taxid_list]
    return taxon_names

if __name__ == "__main__":
    print(list(get_ascendants(1570)))
    print(get_taxid("Lactobacilluss", "genus"))