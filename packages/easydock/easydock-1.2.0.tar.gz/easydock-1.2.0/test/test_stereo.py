from rdkit import Chem
from rdkit.Chem.EnumerateStereoisomers import EnumerateStereoisomers, StereoEnumerationOptions

smi = 'NC(=O)[C@@H]1CC2CC1C2'
mol = Chem.MolFromSmiles(smi)

opts = StereoEnumerationOptions(tryEmbedding=True, maxIsomers=10)
isomers = tuple(EnumerateStereoisomers(mol, options=opts))
print(smi)
for m in isomers:
    print(Chem.MolToSmiles(m))

# list_of_chiral_centers = Chem.FindMolChiralCenters(
#     mol,
#     includeUnassigned=True,
#     useLegacyImplementation=False
# )
# for stereo_atom_idx, stereo_atom_CIP in list_of_chiral_centers:
#     print(stereo_atom_idx, stereo_atom_CIP)
#
# print(smi)
# print(Chem.MolToSmiles(mol))
# for m in get_isomers(mol, 10):
#     print(Chem.MolToSmiles(m))
#     print(Chem.MolToSmiles(Chem.RemoveHs(m)))
#
