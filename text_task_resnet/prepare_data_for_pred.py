import sys
import numpy as np
from prepare_data_for_hred import PrepareData
from params_test_v2 import get_params

start_symbol_index = 0
end_symbol_index = 1
unk_symbol_index = 2
pad_symbol_index = 3
import os


if __name__ == "__main__":
    param = get_params(".", ".", test_state=None)

    test_dir_loc = param['test_dir_loc']
    dump_dir_loc = param['dump_dir_loc']
    vocab_file = param['vocab_file']
    vocab_stats_file = param['vocab_stats_file']
    vocab_freq_cutoff = param['vocab_freq_cutoff']
    test_data_file = param['test_data_file']

    max_utter = param['max_utter']
    max_len = param['max_len']
    max_images = param['max_images']
    preparedata = PrepareData(max_utter, max_len, max_images, start_symbol_index, end_symbol_index, unk_symbol_index,
                              pad_symbol_index, "text", cutoff=vocab_freq_cutoff)
    if os.path.isfile(vocab_file):
        print 'found existing vocab file in ' + str(vocab_file) + ', ... reading from there'
    preparedata.prepare_data(test_dir_loc, vocab_file, vocab_stats_file, os.path.join(dump_dir_loc, "test_smallest"),
                             test_data_file, isTrain=False, isTest=True)
