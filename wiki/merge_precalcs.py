from GraphReader import _bytes_to_int, _int_to_bytes
import sys

N = 5054753
NULL = 2 ** 32 - 1


def get_variants_for_vertex(v, input_filename, input_files_amount):
    easy_variants, medium_variants, hard_variants = [], [], []
    for i in range(input_files_amount):
        current_file = open(input_filename + '_' + str(i), 'rb')
        current_file.seek(v * 4)
        easy_variant = _bytes_to_int(current_file.read(4))
        current_file.seek((N + v) * 4)
        medium_variant = _bytes_to_int(current_file.read(4))
        current_file.seek((2 * N + v) * 4)
        hard_variant = _bytes_to_int(current_file.read(4))
        for current, storage in zip([easy_variant, medium_variant, hard_variant],
                                    [easy_variants, medium_variants, hard_variants]):
            if current != NULL:
                storage.append(current)
    return {'easy': list(set(easy_variants)), 'medium': list(set(medium_variants)), 'hard': list(set(hard_variants))}


files_amount = 1
#print(get_variants_for_vertex(int(sys.argv[1]), 'data/good_end', files_amount))
easy_pairs = []
medium_pairs = []
hard_pairs = []

for v in range(N):
    if v % 1000 == 0:
        print(v, 'ready')
    d = get_variants_for_vertex(v, 'data/good_end', files_amount)
    for u in d['easy']:
        easy_pairs.append([v, u])
    for u in d['medium']:
        medium_pairs.append([v, u])
    for u in d['hard']:
        hard_pairs.append([v, u])

hard = open('data/hard', 'wb')
hard.write(_int_to_bytes(len(hard_pairs)))
for p in hard_pairs:
    hard.write(_int_to_bytes(p[0]))
    hard.write(_int_to_bytes(p[1]))
hard.close()

medium = open('data/medium', 'wb')
medium.write(_int_to_bytes(len(medium_pairs)))
for p in hard_pairs:
    medium.write(_int_to_bytes(p[0]))
    medium.write(_int_to_bytes(p[1]))
medium.close()

easy = open('data/easy', 'wb')
easy.write(_int_to_bytes(len(easy_pairs)))
for p in easy_pairs:
    easy.write(_int_to_bytes(p[0]))
    easy.write(_int_to_bytes(p[1]))
easy.close()