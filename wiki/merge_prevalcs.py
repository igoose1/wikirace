from GraphReader import _bytes_to_int

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
for v in range(N):
    d = get_variants_for_vertex(v, 'data/good_end', files_amount)



        
        
            
        