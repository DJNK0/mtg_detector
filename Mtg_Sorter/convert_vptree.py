import vptree
from main import hamming_distance

with open("C:/Users/david/PycharmProjects/Mtg_Sorter/Hashes/p_hashes", "r") as  hash_file:
    hashes = []
    for line in hash_file:
        line = line.split(':')
        line[-1] = line[-1].strip('\n')
        line[-1] = line[-1].replace(' ', '')
        hashes.append(line[-1])

print('84c499b3fa9363b2'in hashes)

tree = vptree.VPTree(hashes, hamming_distance)
print(tree.get_nearest_neighbor('84e499b1bad963b2'))