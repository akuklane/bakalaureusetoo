import numpy as np
import pandas as pd
import pyranges as pr

from igraph import *
from sklearn.preprocessing import MinMaxScaler
from src.analysis import get_fine_mapping_results
from src.utils.ensure_files_directories import ensure_dir, check_file

'''
Paneb täppiskaardistamise tulemused kokku üheks andmestikuks ja salvestab failina. 
Parameetrid:    dfs -  sõnastik valimisuuruste (võtmed) ja andmestikega (väärtused).
                directory - kataloogitee kokkupandud andmestiku salvestamiseks.
                filename - failinimi kokkupandud andmestiku salvestamiseks.
Väljund: kokkupandud andmestik täppiskaardistamise tulemustest. 
'''
def merge_dataframes(dfs, directory, filename):
    df_merged = pd.DataFrame(columns=['molecular_trait_id', 'variant', 'chromosome', 'position', 'ref', 'alt',
                                      'cs_id', 'cs_index', 'finemapped_region', 'pip', 'z', 'cs_min_r2',
                                      'cs_avg_r2', 'cs_size', 'posterior_mean', 'posterior_sd', 'cs_log10bf'])
    for df_n in dfs:
        df = dfs.get(df_n).copy()

        # lisab hulga ID-le juurde valimi suuruse, millest see pärines
        df['cs_id'] = df['cs_id'] + '_' + str(df_n)
        df_merged = df_merged.merge(df, how='outer')

    ensure_dir(directory)  # kindlustab, et kaust eksisteerib
    df_merged.to_csv(f'{directory}/{filename}')

    return df_merged


'''
Teeb kokkupandud tulemustest pyranges objekti.
Parameetrid:    original_df - täppiskaardistamise tulemuste andmestik.
                filter_cs_size - usaldusväärsete variantide hulga maksimaalne suurus. 
Väljund: andmestikust moodustatud pyranges objekt.
'''
def create_pyranges_object(original_df, filter_cs_size=None):
    df = original_df.copy()
    df = df.filter(['molecular_trait_id', 'chromosome', 'cs_id', 'pip', 'cs_size', 'position'])

    df['End'] = df['position'] + 1 # pyranges jaoks peab positsioon kromosoomil olema vahemikuna
    df = df.rename(columns={"position": "Start", "chromosome": "Chromosome"}) # pyranges jaoks vajalikud veerunimed

    # veergude loogiline järjestamine
    df = df[['molecular_trait_id', 'Chromosome', 'Start', 'End', 'cs_id', 'pip', 'cs_size']]

    # jätab välja kõik hulgad, milles on rohkem variante
    if filter_cs_size is not None:
        df = df[df['cs_size'] < filter_cs_size]

    return pr.from_dict(df.to_dict())  # loob ja tagastab andmestiku pyranges objektina


'''
Leiab ülekattuvad variandid ja salvestab failina.
Parameetrid:    df_pr - pyranges objekt.
                directory - kataloogitee andmestiku salvestamiseks.
                filename - failinimi andmestiku salvestamiseks.
Väljund: leitud paarikaupa ülekattuvate variantide andmestik.
'''
def find_pairs(df_pr, directory, filename):
    # leiab positsioonipõhiselt variantide ülekattuvused
    pairs = df_pr.join(df_pr, report_overlap=True, suffix='_')
    pairs_df = pairs.as_df()  # teeb pyranges objektist dataframe'i

    pairs_df.to_csv(f'{directory}/{filename}')

    return pairs_df


'''
Jätab alles vaid sama geeni ülekattuvad variandid, variantide vahel ühe seose ja salvestab failina, mida kasutatakse 
graafi sisendina. 
Parameetrid:    df - paarikaupa ülekattuvate variantide andmestik.
                directory - kataloogitee töödeldud andmestiku salvestamiseks.
                filename - failinimi töödeldud andmestiku salvestamiseks.
Väljund: töödeldud ülekattuvate variantide andmestik.
'''
def process_result_for_graph(df, directory, filename):
    df = df[['cs_id', 'cs_id_']]  # jätab alles vaid graafi tipud
    df = pd.DataFrame(np.sort(df.values, axis=1),
                      index=df.index).drop_duplicates()  # jätab kahe tipu vahel alles vaid ühe serva
    df = df.rename(columns={0: 'cs_id', 1: 'cs_id_'})
    print(df.shape)
    df = df[df['cs_id'].str[0:15] == df['cs_id_'].str[0:15]]  # jätab alles servad vaid sama geeni tippude vahel
    print(df.shape)
    df.to_csv(f'{directory}/{filename}')

    return df


'''
Ülekattes olevatest variantidest graafi moodustamine.
Parameetrid:    df - kahest veerust koosnev andmestik graafi loomiseks.
Väljund: ülekattes olevatest variantidest moodustatud graaf.
'''
def get_graph(df):
    assert len(df.columns) == 2

    #  andmestiku veergudes on ülekattes olevad variandid, mis on graafi tippudeks
    graph = Graph.TupleList(df.itertuples(index=False), directed=False, vertex_name_attr='label')
    #print(f'Moodustati graaf {graph.vcount()} tipu ja {graph.ecount()} servaga.')

    return graph


'''
Leiab graafi komponendid.
Parameetrid:    graph - ülekattuvatest variantidest moodustatud graaf.
Väljund: graafi komponendid ja komponentide pikkuste järjend.
'''
def get_components(graph):
    graph_components = graph.clusters()  # leiab graafi komponendid

    # lisame kõik komponendid listi
    components = [list(component) for component in graph_components]

    # leiab järjendina komponentide suurused
    component_sizes = sorted([len(component) for component in graph_components], reverse=True)

    # print(component_sizes)
    # largest = graph_components.giant()

    return components, component_sizes


'''
Moodustab komponentidest koosneva andmestiku.
Parameetrid:    graph - ülekattuvatest variantidest moodustatud graaf.
                pairs_df - ülekattuvate variantide paarid.
                components - järjend graafi komponentidest. 
                components_sizes - komponentide suurused.
                directory - kataloogitee komponentide andmestiku salvestamiseks.
                filename - failinimi komponentide andmestiku salvestamiseks.
Väljund: komponentide andmestik.
'''
def components_to_df(graph, pairs_df, components, components_sizes, directory, filename):
    column_names = []
    max_size = max(components_sizes)

    for size in [100, 200, 300, 358, 966]:  # tekitame iga valimi suuruse juurde mitu hulka, kuna igal valimisuurusel võib olla
        for cs_index in range(1, 9):  # geenil kuni kaheksa usaldusväärsete variantide hulka (indeksitega L1-L8)
            column_names.append(f'cs_id_{size}_{cs_index}')
            column_names.append(f'cs_id_{size}_{cs_index}_size')

    df = pd.DataFrame(columns=column_names)

    for component in components:  # lisame andmestikku kõik graafi komponendid
        component_size = len(component)  # leiab, mitu hulka on komponendis
        comp_size = 0  # suurus, mis näitab mitmele valimisuurusele vastab vähemalt üks hulk (maksimaalne suurus == 5)

        result = {}  # töödeldud komponendi hoidmiseks ja lisamiseks dataframe'i
        values = {100: [], 200: [], 300: [], 358: [], 966: []}

        # leiab komponendis olevate hulkade ID-d ja vastavad suurused
        for i in range(max_size):
            if i < component_size:
                cs_id = graph.vs[component[i]]["label"]  # hulga ID
                cs_size = np.array(pairs_df[pairs_df['cs_id'] == cs_id]['cs_size'])[0]  # hulga suurus
                values[int(cs_id[-3:])].append((cs_id, cs_size))  # lisab valimi suurusele vastavasse järjendisse
            else:
                break

        for size in values:
            if len(values[size]) == 0:  # valimisuurusel # ei leitud ühtegi hulka
                for cs_index in range(1, 9):  # lisab konkreetsel valimisuurusel indeksveergudesse puuduva väärtuse
                    result[f'cs_id_{size}_{cs_index}'] = np.nan
                    result[f'cs_id_{size}_{cs_index}_size'] = np.nan

            else:  # leidub vähemalt üks valimi suurusele vastav hulk
                values[size].sort(key=lambda x: x[0])  # sorteerib hulgad vastavalt indeksile (L1-L8)
                comp_size += 1  # valimisuurusel leidub vähemalt üks hulk
                cs_indices = [1, 2, 3, 4, 5, 6, 7, 8]

                for _tuple in values[size]:  # vaatab läbi kõik valimisuurusel leitud hulgad ja suurused
                    cs_index = int(_tuple[0][-5])
                    result[f'cs_id_{size}_{cs_index}'] = _tuple[0]  # lisab hulga vastavale valimi suurusele ja indeksile
                    result[f'cs_id_{size}_{cs_index}_size'] = _tuple[1] # lisab hulga suuruse vastavale valimi suurusele ja indeksile

                    if cs_index not in cs_indices:  # eemaldab hulgast indeksi, millele ei ole vaja hiljem puuduvat
                        cs_indices.remove(cs_index)  # ID ja suuruse väärtust lisada

                if len(cs_indices) > 0:  # puuduvate väärtuste lisamine indeksitele, millele ei olnud vastavat hulka
                    for cs_index in cs_indices:
                        result[f'cs_id_{size}_{cs_index}'] = np.nan
                        result[f'cs_id_{size}_{cs_index}_size'] = np.nan

        result['cluster_size'] = comp_size  # mitmele valimisuurusele vastas vähemalt üks hulk
        result['component_size'] = component_size  # mitu hulka oli komponendis kokku
        df = df.append(result, ignore_index=True)

    df.to_csv(f'{directory}/{filename}')

    return df


'''
Andmestiku numbriliste veergude normaliseerimine (teisendamine 0 ja 1 vahele) ridade kaupa. 
Parameetrid:    df - komponentidest koosnev andmestik.
Väljund: komponentide normaliseeritud andmestik.
'''
def normalize_df(df):
    colnames = ['100', '200', '300', '358', '966']  # teisendatavad veerud

    scaler = MinMaxScaler()  # väärtuste teisendamine 0 ja 1 vahele (normaliseerimine)

    vals = df[colnames].values.T  # andmestiku transponeerimine, et seda reakaupa normaliseerida
    vals_scaled = scaler.fit_transform(vals)  # väärtuste teisendamine

    df_scaled = pd.DataFrame(vals_scaled.T, columns=colnames, index=df.index)
    df[colnames] = df_scaled  # asendab vastavate veergude väärtused uute teisendatud väärtustega

    return df


'''
Andmestikust kõrvalekallete eemaldamine.
Parameetrid:    df - töödeldav andmestik.
                columns - veerud, mille põhjal kõrvalekaldeid eemaldada.
                max_bound - komponentides sisalduvate hulkade maksimaalne suurus.
Väljund: töödeldud andmestik, kus on etteantud piirist väiksema suurusega hulgad.
'''
def remove_components(df, columns, max_bound):

    # vaatab läbi kõik veerud, kust kõrvalekalded eemaldada
    for column in columns:
        df = df[df[column] < max_bound]  # jätame veerus alles read, kus hulgad on etteantud piirist väiksemad
        rows = df.shape[0]
        df = df.reindex(np.arange(0, rows))  # reindekseerimine

    return df


'''
Komponentide andmestikust puuduvate väärtuste eemaldamine, komponendis erinevatele indeksitele vastavate hulkade 
eraldamine ja töödeldud andmestiku salvestamine. 
Parameetrid:    df - komponentide töötlemata andmestik.
                directory - kataloogitee töödeldud komponentide andmestiku salvestamiseks.
                filename - failinimi töödeldud komponentide andmestiku salvestamiseks.
Väljund: komponentide töödeldud andmestik.
'''
def process_components_df(df, directory, filename):
    df_original = df.copy()

    # jätab alles kuuest vähema hulgaga komponendid
    df_original = df_original[df_original['component_size'] < 6]

    sample_sizes = [100, 200, 300, 358, 966]
    colnames = []

    for size in sample_sizes:
        colnames.append(f'cs_id_{size}')
        colnames.append(f'{size}')

    colnames.append('cluster_size')

    df_original = df_original.drop(columns=['cluster_size', 'component_size'])
    df_processed = pd.DataFrame(columns=colnames)

    # vaatab andmestikku vastavalt indeksitele
    for i in range(1, 9):
        # filteerib välja indeksid, millele ei vastanud ühtegi hulka
        df = df_original[(df_original[f'cs_id_100_{i}'].notnull()) | (df_original[f'cs_id_200_{i}'].notnull()) |
                         (df_original[f'cs_id_300_{i}'].notnull()) | (df_original[f'cs_id_358_{i}'].notnull()) |
                         (df_original[f'cs_id_966_{i}'].notnull())].copy()

        # leiab hulga indeksile vastavad veerunimed
        columns = [column for column in df.columns if column[-1] == str(i) or f'_{i}_' in column]
        df = df[columns]  # filtreerib andmestikku vastavalt indeksit sisaldavatele veerunimedele

        for size in sample_sizes:
            df.rename(columns={f'cs_id_{size}_{i}': f'cs_id_{size}', f'cs_id_{size}_{i}_size': f'{size}'}, inplace=True)

        for k in range(df.shape[0]):
            row = df.iloc[k].dropna()  # viskab reast välja kõik puuduvad väärtused

            # mitmele valimisuurusele leiti hulk (kahega jagamine arvestab ridades välja hulga ID-d)
            row.at['cluster_size'] = len(row.values) / 2

            for size in sample_sizes:  # kui mingil valimisuurusel puudus hulga indeksile vastav väärtus, siis lisatakse
                if str(size) not in row:  # puuduv väärtus
                    row.at[f'{size}'] = np.nan
                    row.at[f'cs_id_{size}'] = np.nan

            row.sort_index()
            df_processed = df_processed.append(row, ignore_index=True) # lisab töödeldud rea uude dataframe'i

    df_processed.to_csv(f'{directory}/{filename}')

    return df_processed


'''
Leiab geenid, millele vastab komponent suurusega n, ja salvestab geenile vastavad usaldusväärsete variantide hulgad failina.
Parameetrid:    components_df - komponentide andmestik.
                n - komponendi suurus.
                directory - kataloogitee faili(de) salvestamiseks.
'''
def extract_components_with_size_n_to_dfs(components_df, n, directory):
    file = os.getcwd() + '/data/processed-results/' + 'RESULTS_merged.purity_filtered.txt'
    check_file(file)

    # fail geenile vastavate hulkade ja hulkades sisalduvate variantide leidmiseks
    merged_df = pd.read_csv(file, sep=',')

    # leiame andmesitkust kõik komponendid suurusega n
    components_df = components_df[components_df['component_size'] == n].drop(['Unnamed: 0', 'component_size', 'cluster_size'], axis=1)
    id_columns = [column for column in components_df.columns if ('size' not in column)]
    genes = set()

    # leiab geenid, mis sisalduvad komponentides suurusega n
    for column in id_columns:
        components_column = components_df[column]
        column_cs_ids = components_column[~components_column.isnull()].values
        column_gene_ids = [ids[:15] for ids in column_cs_ids]  # eraldab hulga ID-st geeni ID

        genes.update(set(column_gene_ids))

    ensure_dir(directory)

    for gene in genes:
        df = merged_df[merged_df['molecular_trait_id'] == gene]
        df.to_csv(f'{directory}/{n}_{gene}.csv', index=False)


'''
Eemaldab andmestikust kõrvalekalded ja normaliseerib numbriliste veergude väärtused joondiagrammi jaoks.
Parameetrid:    df_original - andmestik.
                sample_sizes - järjend valimisuurustest sõnedena. 
                max_bound - komponentides sisalduvate hulkade maksimaalne suurus.
Väljund: töödeldud andmestik.
'''
def process_df_lineplot(df_original, sample_sizes, max_bound=None):
    df = df_original.copy()

    # eemaldab komponendid, milles leidus vähemalt üks hulk, mis oli etteantud piirist suurem
    if max_bound is not None:
        df = remove_components(df, sample_sizes, max_bound)

    normalized_df = normalize_df(df)  # andmestiku väärtuste reakaupa teisendamine 0 ja 1 vahele

    return normalized_df


'''
Andmestiku töötlemine viiuldiagrammi jaoks.
Parameetrid:    df_original - andmestik.
                sample_sizes - valimisuuruste veerunimed.
                size - arv, mis näitab, mitmel valimisuurusel peab leiduma hulk (maksimaalne arv == 5f)
                max_bound - komponentides sisalduvate hulkade maksimaalne suurus.
Väljund: töödeldud andmestik.
'''
def process_df_violinplot(df_original, sample_sizes, size, max_bound=None):
    df = df_original.copy()
    df = df[df['cluster_size'] == size]  # jätab komponendid, mis leidusid täpselt n valimisuurusel

    df = df[sample_sizes]  # jätab alles ainult numbrilised veerud (hulkade suurused)

    # eemaldab komponendid, milles leidus vähemalt üks hulk, mille suurus ületas etteantud piiri
    if max_bound is not None:
        df = remove_components(df, sample_sizes, max_bound)

    return df


if __name__ == '__main__':
    dfs = get_fine_mapping_results()  # loeb sisse täppiskaardistamise tulemused

    # kaust kokkupandud andmestiku salvestamiseks ja komponentide analüüsi käigus loodud failide salvestamiseks
    directory = os.getcwd() + '/data/processed-results'

    # paneb täppiskaardistamise tulemusena saadud failid kokku
    merged_df = merge_dataframes(dfs, directory, 'RESULTS_MERGED.purity_filtered.txt')

    df_pr = create_pyranges_object(merged_df)  # teeb andmestikust pyranges objekti
    pairs_df = find_pairs(df_pr, directory, 'pyranges_pairs.csv')  # leiab ülekattuvate variantide paarid

    del df_pr, merged_df  # mälu kokkuhoid

    # loob pyranges tulemusest graafi tipud
    tuple_df = process_result_for_graph(pairs_df, directory, 'pyranges_pairs_processed.csv')

    graph = get_graph(tuple_df)  # teeb graafi

    del tuple_df

    components, sizes = get_components(graph) # leiab graafi komponendid

    # moodustab graafi komponentidest dataframe'i
    components_df = components_to_df(graph, pairs_df, components, sizes, directory, 'components.csv')
    process_components_df(components_df, '', 'components_processed.csv') # töötleb komponentide andmestikku

    del components, pairs_df

    # directory = os.getcwd() + '/data/processed-results/sample-genes'
    # n = 7
    # eraldab komponentides suurusega n geenile vastavad hulgad eraldi failiks
    # extract_components_with_size_n_to_dfs(components_df, n, directory)
