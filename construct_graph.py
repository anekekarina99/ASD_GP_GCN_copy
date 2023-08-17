import os
import argparse
import pandas as pd
from nilearn.datasets import fetch_abide_pcp
from nilearn.datasets.utils import _fetch_file
from construct_graph import construct_brain_graph

# Parsing argumen dari command line
parser = argparse.ArgumentParser()
parser.add_argument('--root', type=str, default='./data', help='Path to store the brain graphs')
parser.add_argument('--verbose', type=bool, default=True, help='Print the download details')
args = parser.parse_args()

# Fungsi untuk menghapus path atau file
def delete_path(path):
    if os.path.exists(path):
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)

if __name__ == '__main__':
    # Mendownload dataset ABIDE I yang telah diproses oleh CPAC
    fetch_abide_pcp(data_dir='./temp', derivatives='rois_ho', verbose=args.verbose,
                   pipeline='cpac', band_pass_filtering=True, global_signal_regression=True)
    
    # Path yang dihasilkan oleh fetch abide
    path = os.path.join('./temp', 'ABIDE_pcp', 'cpac', 'filt_global')

    # Path untuk menyimpan informasi fenotipe
    info_path = os.path.join(args.root, 'phenotypic')
    if not os.path.exists(info_path):
        os.makedirs(info_path)

    # Memuat informasi fenotipe
    phenotypic = pd.read_csv(os.path.join('./temp', 'ABIDE_pcp', 'Phenotypic_V1_0b_preprocessed1.csv'))
    logs = load_text(path, phenotypic)

    # Menyesuaikan nilai label
    logs['label'] = [2 - i for i in logs['DX_GROUP']]
    logs.to_csv(os.path.join(args.root, 'phenotypic', 'log.csv'))

    # Mendownload label atlas HO
    src_path = 'https://s3.amazonaws.com/fcp-indi/data/Projects/ABIDE_Initiative/Resources/ho_labels.csv'
    _fetch_file(src_path, info_path)
    atlas = pd.read_csv(os.path.join(info_path, 'ho_labels.csv'), comment='#', header=None, names=['index', 'area'])

    # Membangun representasi graf otak
    construct_brain_graph(logs, atlas, os.path.join(args.root, 'ABIDE', 'raw'), path)

    # Menghapus data yang telah diunduh
    delete_path('./temp')
