import os
import glob
from Bio import SeqIO


file_dir    = 'AOA_2279_dRep99_1679_for_mapping_renamed'
file_ext    = 'fna'
op_dir      = 'AOA_2279_dRep99_1679_for_mapping_renamed_2kbp'


file_re = '%s/*.%s' % (file_dir, file_ext)
file_list = glob.glob(file_re)

for each_file in file_list:
    file_name = os.path.basename(each_file)
    op_file = '%s/%s' % (op_dir, file_name)
    op_file_handle = open(op_file, 'w')
    for each_seq in SeqIO.parse(each_file, 'fasta'):
        if len(each_seq.seq) >= 2000:
            op_file_handle.write('>%s\n' % each_seq.id)
            op_file_handle.write('%s\n'  % each_seq.seq)
        else:
            print(each_seq.id)
    op_file_handle.close()
