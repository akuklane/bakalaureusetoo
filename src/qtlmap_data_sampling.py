import pandas as pd

from src.qtlmap_data_preprocessing import preprocess_metadata_df
from src.utils.ensure_files_directories import *

'''
Loeb sisse andmestiku.  
Parameetrid:    filepath - failitee andmestikuni. 
Väljund: andmestik. 
'''
def get_dataset_df(filepath):
    file = filepath + '.tsv'

    if check_file(file):
        return pd.read_csv(file, sep='\t')


'''
Loob andmestiku alamhulga, milles on n proovi.
Parameetrid:    df - andmestik.
                n - valimi suurus.
Väljund: etteantud andmestiku n proovist juhuslikult moodustatud andmestik. 
'''
def generate_file_with_size(df, n):
    return df.sample(n).sort_index()


'''
Kvaliteedikontrolli läbitud Euroopa alamhulga andmestiku ja alamandmestike .csv failideks tegemine.
Parameetrid:    filename - andmestiku failinimi.
                sample_sizes - alamandmestike suurused.
'''
def subset_metadata_file(filename, sample_sizes):
    filepath = os.getcwd() + '/data/qtlmap-inputs/metadata/' + filename
    df = get_dataset_df(filepath)  # loeb sisse andmestiku dataframe kujul

    processed_df = preprocess_metadata_df(df, filename)  # andmestiku eeltöötlus
    sample_sizes.append(
        processed_df.shape[0])  # lisab Euroopa indiviide alamhulga täissuuruse valimi suuruste järjendisse

    change_dir(os.getcwd() + '/data/qtlmap-inputs/metadata-processed/')

    for size in sample_sizes:
        sample_df = generate_file_with_size(processed_df, size)  # andmestik juhuslikult valitud n prooviga
        sample_df.to_csv(f'{filename}_{str(size)}.tsv', sep='\t', index=False)  # salvestab andmestiku failina

        print(f'Generating sample from {filename} with size {str(size)}')

    print('\nGeneration of samples complete.')


if __name__ == '__main__':
    os.chdir('..')
    subset_metadata_file('GEUVADIS', [100, 200, 300])  # failide genereerimine
