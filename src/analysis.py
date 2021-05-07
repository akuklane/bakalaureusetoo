import os
import pandas as pd

from src.utils.ensure_files_directories import check_files

'''
Loeb sisse täppiskaardistamise tulemusel saadud failid.
Väljund: sõnastik valimisuuruste (võtmed) ja andmestikega (väärtused).
'''
def get_fine_mapping_results():
    os.chdir('..')
    directory = os.getcwd() + '/data/fine-mapping-results/'

    files = sorted([file for file in os.listdir(directory) if not file.startswith('.')])
    sample_sizes = [100, 200, 300, 358, 966]

    dfs = {}
    if check_files(directory, files):
        for i, size in enumerate(sample_sizes):
            dfs[size] = pd.read_csv(directory + files[i], sep='\t')

    return dfs


'''
Leiab andmestikes leiduvate usaldusväärsete variantide hulkade koguarvud. 
Parameetrid:    dfs - sõnastik valimisuuruste (võtmed) ja andmestikega (väärtused).
Väljund: järjend hulkade koguarvudest.
'''
def get_number_of_cs(dfs):
    cs_sizes = []

    for df in dfs:
        df_copy = dfs.get(df).copy().drop_duplicates(subset='cs_id',  # jätab kõikidest usaldusväärsete variantide
                                                     keep='first')  # hulka kuuluvatest variantidest alles vaid ühe
        # allesjäänud variandid on 1:1 suhtes hulkadega, seega hulkade koguarv on võrdne ridade arvuga
        cs_n = df_copy.shape[0]
        cs_sizes.append(cs_n)

    return cs_sizes


'''
Leiab andmestikes geenide arvud, millele vastas n või rohkem usaldusväärsete variantide hulka.  
Parameetrid:    dfs - sõnastik valimisuuruste (võtmed) ja andmestikega (väärtused).
                nr_cs - geenile vastavate hulkade minimaalne arv.
Väljund: järjend geenide koguarvudest.
'''
def get_number_of_genes_with_n_cs(dfs, nr_cs):
    n_genes = []

    for df in dfs:
        df_copy = dfs.get(df).copy().drop_duplicates(subset='cs_id',  # jätab kõikidest usaldusväärsete variantide
                                                     keep='first')  # hulka kuuluvatest variantidest alles vaid ühe
        value_counts = df_copy['molecular_trait_id'].value_counts()  # leiab, mitu korda geen andmestikus esineb
        count = value_counts[value_counts >= nr_cs].shape[
            0]  # geenide arv, millele vastab n või rohkem variantide hulka
        n_genes.append(count)

    return n_genes


'''
Leiab andmestikes usaldusväärsete variantide hulkade suuruse mediaani/keskmise.
Parameetrid:    dfs - sõnastik valimisuuruste (võtmed) ja andmestikega (väärtused).
                median - True: keskmist arvutatakse kasutades mediaani (vaikeväärtus), 
                         False: keskmist arvutatakse kasutades aritmeetilist keskmist.
Väljund: järjend hulkade mediaanidest/keskmistest suurustest.
'''
def get_average_size_of_cs(dfs, median=True):
    avg_sizes = []

    for df in dfs:
        cs_sizes = \
            dfs.get(df).copy().drop_duplicates(subset='cs_id',  # jätab kõikidest usaldusväärsete variantide hulka
                                               keep='first')['cs_size']  # kuuluvatest variantidest alles vaid ühe
        if median:
            avg_cs_size = cs_sizes.median()  # leiab mediaani
        else:
            avg_cs_size = cs_sizes.mean()  # leiab aritmeetilise keskmise

        avg_cs_size = round(avg_cs_size)
        avg_sizes.append(avg_cs_size)

    return avg_sizes


'''
Loob arvujärjendist suurusvahemikud.
Parameetrid:    bins - järjend vahemike esimestest arvudest.
Väljund: järjend suurusvahemikest.
'''
def create_keys(bins):
    bins.sort()
    processed_bins = []

    for i, key in enumerate(bins):
        if i == len(bins) - 1:
            processed_bins.append(
                f'{key}+')  # kui viimane arv, siis luuakse võti kujul <arv>+ (kõik suuremad arvud)
        elif key + 1 == bins[i + 1]:
            processed_bins.append(str(key))  # kui järgmise suurusvahemiku algus on arv suurem, siis vahemik on 1 arv
        else:
            processed_bins.append(f'{str(key)}-{bins[i + 1] - 1}')

    return processed_bins


'''
Leiab valimisuurustele vastavalt hulkade arvu erinevates suurusvahemikes. 
Parameetrid:    dfs -  sõnastik valimisuuruste (võtmed) ja andmestikega (väärtused).
                bins - järjend suurusvahemike esimestest arvudest.
Väljund: andmestik, kus andmeread sisaldavad kindlat valimisuurust ja suurusvahemikku ning valimisuurusel leitud CS-ide 
         arvu selles suurusvahemikus. 
'''
def get_bins_of_cs_sizes(dfs, bins=None):
    if bins is None:
        bins = [1, 2, 6, 16, 26, 50]

    x_col = 'CS-ide suurused'
    y_col = 'CS-ide arv'

    df = pd.DataFrame(columns=['Sample_size', x_col, y_col])
    keys = create_keys(bins)  # loob suurusvahemikud (võtmed)

    for df_n in dfs:
        df_copy = dfs.get(df_n).copy().drop_duplicates(subset='cs_id', keep='first')

        for i in range(len(bins)):
            # leiab mitu usaldusväärsete variantide hulka leidus vahemikus
            if i == len(bins) - 1:
                count = df_copy[df_copy['cs_size'] >= bins[i]].shape[0]
                df = df.append({'Sample_size': df_n, x_col: keys[i], y_col: count}, ignore_index=True)
            else:
                count = df_copy[(df_copy['cs_size'] >= bins[i]) & (df_copy['cs_size'] < bins[i + 1])].shape[0]
                df = df.append({'Sample_size': df_n, x_col: keys[i], y_col: count}, ignore_index=True)

    return df


'''
Leiab valimisuurustele vastavalt usaldusväärsete variantide hulka arvu vastavalt hulga indeksile (L1, L2, ..., L8). 
Parameetrid:    dfs -  sõnastik valimisuuruste (võtmed) ja andmestikega (väärtused).
Väljund: sõnastik valimisuuruste (võtmed) ja hulkade koguarvudega sõltuvalt indeksist.
'''
def get_cs_index_counts(dfs):
    index_counts = {}

    for df_n in dfs:
        df = dfs.get(df_n).copy().drop_duplicates(subset='cs_id',  # jätab kõikidest usaldusväärsete variantide hulka
                                                  keep='first')  # kuuluvatest variantidest alles vaid ühe
        counts = []  # järjend hulkade arvude hoidmiseks
        # leiame, mitu hulka on indeksiga i ja lisame järjendisse
        [counts.append(df[df['cs_index'] == f'L{i}'].shape[0]) for i in range(1, 9)]
        index_counts[df_n] = counts  # valimisuurus (võti) : hulkade koguarvud (väärtus)

    return index_counts


if __name__ == '__main__':
    dfs = get_fine_mapping_results()  # loeb sisse täppiskaardistamise tulemused

    number_of_cs = get_number_of_cs(dfs)
    print('Valimisuurustele 100, 200, 300, 358 ja 966 leiti vastavalt', number_of_cs,
          'usaldusväärsete variantide hulka.')

    number_of_genes = get_number_of_genes_with_n_cs(dfs, 2)
    print('\nValimisuurustele 100, 200, 300, 358 ja 966 leiti vastavalt', number_of_genes,
          'geeni, millele leidus rohkem kui 2 usaldusväärsete variantide hulka.')

    average_sizes_of_cs = get_average_size_of_cs(dfs)
    print('\nValimisuurustel 100, 200, 300, 358 ja 966 oli keskmine usaldusväärsete variantide '
          'hulga suurus vastavalt', average_sizes_of_cs)

    bins_cs_sizes_df = get_bins_of_cs_sizes(dfs)
    print('\nUsaldusväärsete variantide hulkade arvud erinevates suurusvahemikes vastavalt valimisuurusele:\n',
          bins_cs_sizes_df.head(30), '\n')

    index_counts = get_cs_index_counts(dfs)
    print('Usaldusväärsete variantide hulkade indeksite L1-L8 sagedused erinevate valimisuuruste puhul:', index_counts)
