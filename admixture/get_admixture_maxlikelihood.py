import os, sys
import numpy as np
import subprocess
from pathlib import Path


def read_likelihood(input_file):
    f = open(input_file)
    likelihood = 0
    target_line = [li for li in f if li.startswith("Loglikelihood")]
    if len(target_line) > 0:
        likelihood = target_line[-1].rstrip("\n").split()[-1]
    return float(likelihood)


def get_max(file_list):
    likelihoods = []
    valid_files = []
    for fi in file_list:
        if os.path.exists(fi):
            likelihood = read_likelihood(fi)
            if not likelihood == 0:
                valid_files.append(fi)
                likelihoods.append(likelihood)
    if len(likelihoods) < 1:
        print("Warning: No valid file")
    # print(likelihoods)
    # print(valid_files)
    max_likelihood = np.argsort(np.array([likelihoods]))
    max_likelihood_file = valid_files[max_likelihood[0][-1]]
    return max_likelihood_file, max_likelihood


# file_list = sys.argv[1:]
log_folder, qmat_folder, select_folder, start_k, end_k = sys.argv[1:]
for k in range(int(start_k), int(end_k)+1):
    file_list = list(Path(log_folder).glob("K{}.*.log".format(k)))
    max_likelihood_file, max_likelihood = get_max(file_list)
    tag = str(max_likelihood_file).split("/")[-1]
    cmd = "cp {}/{}.* {}/".format(qmat_folder, tag.replace(".log", ""), select_folder)
    subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
# print(max_likelihood_file)
# print(max_likelihood_file, max_likelihood)
