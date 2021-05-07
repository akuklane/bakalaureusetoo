import pandas as pd

from ordered_set import OrderedSet

'''
Eeltöötleb metaandmete andmestikku vastavalt nimele (GEUVADIS, GENCORD, TwinsUK).
Parameetrid:    df - metaandmete andmestik.
                dataset_name - andmestiku nimi. 
Väljund: eeltöödeldud andmestik. 
'''
def preprocess_metadata_df(df, dataset_name):
    if dataset_name == 'GEUVADIS':
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)  # eemaldab sõne ees ja järel olevad tühikud

        # teisendab sõne kujul tõeväärtused boolean tüübiks
        df['rna_qc_passed'] = df['rna_qc_passed'].map({'TRUE': True, 'FALSE': False})
        df['genotype_qc_passed'] = df['genotype_qc_passed'].map({'TRUE': True, 'FALSE': False})

        # tagastab kvaliteedikontrolli läbinud Euroopa päritolu indiviidide proovid
        return df[(df['rna_qc_passed']) & (df['genotype_qc_passed']) & (df['superpopulation_code'] == 'EUR')]

    elif dataset_name == 'GENCORD' or dataset_name == 'TwinsUK':
        # tagastab kvaliteedikontrolli läbinud LCL rakutüübist indiviidide proovid
        return df[(df['cell_type'] == 'LCL') & (df['rna_qc_passed']) & (df['genotype_qc_passed'])]

    else:
        # andmestik ei olnud GEUVADIS, GENCORD või TwinsUK
        raise ValueError(f'Invalid dataset_name: {dataset_name}')


'''
Paneb andmestike metaandmete failid kokku ja salvestab failina. 
Parameetrid:    geuvadis_metadata_df - GEUVADIS metaandmete andmestik.
                gencord_metadata_df - GENCORD metaandmete andmestik. 
                twinsuk_metadata_df - TwinsUK metaandmete andmestik.
                filepath - failitee kokkupandud metaandmete faili salvestamiseks. 
Väljund: kolme andmestiku metaandmetest kokkupandud andmestik.  
'''
def merge_metadata_dfs(geuvadis_metadata_df, gencord_metadata_df, twinsuk_metadata_df, filepath):
    geuvadis_metadata_df = geuvadis_metadata_df.rename(columns={'sex   ': 'sex', 'study   ': 'study'})

    geuvadis_columns = list(geuvadis_metadata_df.columns)
    gencord_columns = list(gencord_metadata_df.columns)
    twinsuk_columns = list(twinsuk_metadata_df.columns)

    all_columns = list(OrderedSet(gencord_columns + geuvadis_columns + twinsuk_columns))  # veergude ühisosa
    overlaping_columns = []

    for column in all_columns:
        # lisame veeru järjendisse, kui see on olemas kõikides andmestikes
        if column in geuvadis_columns and column in gencord_columns and column in twinsuk_columns:
            overlaping_columns.append(column)

    df = pd.DataFrame(columns=overlaping_columns)

    # paneme metaandmete failide kattuvad veerud kokku üheks andmestikuks
    metadata_merged = df.append([geuvadis_metadata_df[overlaping_columns],
                                    gencord_metadata_df[overlaping_columns],
                                    twinsuk_metadata_df[overlaping_columns]])
    metadata_merged.to_csv(filepath, sep='\t', index=False)

    return metadata_merged


'''
Paneb andmestike geeniekspressioonimaatriksid kokku.
Parameetrid:    geuvadis_ge_df - GEUVADIS geeniekspressioonimaatriks.
                gencord_ge_df - GENCORD geeniekspressioonimaatriks.
                twinsuk_ge_df - TwinsUK geeniekspressioonimaatriks.
Väljund: kolme andmestiku geeniekspressioonimaatriksitest kokkupandud maatriks.
'''
def merge_gene_expression_dfs(geuvadis_ge_df, gencord_ge_df, twinsuk_ge_df):
    ge_merged = geuvadis_ge_df.merge(gencord_ge_df, on='phenotype_id')
    ge_merged = ge_merged.merge(twinsuk_ge_df, on='phenotype_id')

    return ge_merged


'''
Töötleb geeniekspressioonimaatriksit ja salvestab failina.
Parameetrid:    ge_df - andmestike ühine geeniekspressioonimaatriks.
                metadata_df - metaandmete ühine andmestik. 
                filepath - failitee töödeldud maatriksi salvestamiseks.
Väljund: töödeldud geeniekspressioonimaatriks.
'''
def process_merged_gene_expression_df(ge_df, metadata_df, filepath):
    sample_ids = list(metadata_df['sample_id'])
    columns_to_drop = []

    for column in ge_df.columns[1:]:  # vaatab kõiki veerge peale indeksveeru
        if column not in sample_ids:
            columns_to_drop.append(column)

    # jätab välja kõik indiviidide proovid, mis jäeti välja ka metaandmete failis
    ge_df = ge_df.drop(columns=columns_to_drop)
    ge_df.to_csv(filepath, sep='\t', index=False)

    return ge_df
