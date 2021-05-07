import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from igraph import *
from src.utils.ensure_files_directories import ensure_dir

'''
Ülekattes olevate hulkade graafi joonistamine. 
Parameetrid:    g - graaf.
                visual_style - joonise kujunduse atribuudid.
                figname - failinimi joonise salvestamiseks.
'''
def plot_graph(g, visual_style=None, figname=None):
    if visual_style is None:
        visual_style = {'vertex_size': 40, 'vertex_label_size': 30, 'layout': g.layout('large'), 'bbox': (5000, 5000),
                        'margin': 300}

    # joonise salvestamine
    if figname is not None:
        os.chdir('..')
        root_dir = os.getcwd()

        ensure_dir(root_dir + '/figures/')
        os.chdir(root_dir + '/figures/')

        plot(g, figname, **visual_style)
        os.chdir(root_dir + '/src/')
    else:
        plot(g, **visual_style)


'''
Graafiku kujundamine. 
Parameetrid:    plot_params - graafiku atribuudid.
Väljund: esialgse graafiku joonis (fig) ja teljed (ax).
'''
def create_plot(plot_params):
    fig, ax = plt.subplots(figsize=plot_params['figsize'])

    plt.rcParams['font.size'] = plot_params['fontsize']
    plt.xticks(fontsize=plot_params['ticks_size'])
    plt.yticks(fontsize=plot_params['ticks_size'])

    ax.tick_params(axis='both', pad=15)
    ax.margins(plot_params['margins'][0], plot_params['margins'][1])
    ax.set_xlabel(plot_params['x_label'], fontsize=plot_params['label_fontsize'], labelpad=plot_params['label_padding'])
    ax.set_ylabel(plot_params['y_label'], fontsize=plot_params['label_fontsize'], labelpad=plot_params['label_padding'])

    return fig, ax


'''
Valimite suurustele vastavate tulemuste (CS-ide koguarvude, mediaanide jms) kujutamine tulpdiagrammil. 
Parameetrid:    plot_params - tulpdiagrammi kujunduse atribuudid.
                x - järjend x-telje väärtustest.
                y - järjend y-telje väärtustest.
                figname - failinimi joonise salvestamiseks.
Väljund: graafiku joonis (fig) ja teljed (ax).
'''
def draw_barplot(plot_params, x, y, figname):
    fig, ax = create_plot(plot_params)

    x_label = plot_params['x_label']
    y_label = plot_params['y_label']

    df = pd.DataFrame({x_label: x, y_label: y})
    ax = sns.barplot(x=x_label, y=y_label, data=df, ax=ax,
                     palette=['#5975a4', '#cc8963', '#5f9e6e', '#b55d60', '#857aab'])

    # annotatsioonide lisamine joonisele
    for patch in ax.patches:
        ax.annotate(format(round(patch.get_height())), (patch.get_x() + patch.get_width() / 2.,
                                                      patch.get_height() + plot_params['annotation_offset']),
                    ha='center', va='center',xytext=(0, 9), textcoords='offset points')

    # joonise salvestamine
    fig.savefig(os.getcwd() + '/figures/' + figname)

    return fig, ax


'''
Valimite suurustele vastavates erinevates suurusvahemikes olevate hulkade arvude kujutamine tulpdiagrammil.
Parameetrid:    plot_params - tulpdiagrammi kujunduse atribuudid.
                df - andmestik valimisuuruste, suurusvahemike ja suurusvahemikes olevate CS-ide koguarvudega.
                figname - failinimi joonise salvestamiseks.
Väljund: graafiku joonis (fig) ja teljed (ax).
'''
def draw_grouped_barplot(plot_params, df, figname=None):
    fig, ax = create_plot(plot_params)

    x_label = plot_params['x_label']
    y_label = plot_params['y_label']

    ax = sns.barplot(x=x_label, y=y_label, hue='Sample_size', data=df)
    legend = ax.legend(fontsize='medium', bbox_to_anchor=(1.05, 1), loc='upper left', facecolor='white', framealpha=1)

    # joonise salvestamine
    fig.savefig(os.getcwd() + '/figures/' + figname, bbox_extra_artists=(legend,), bbox_inches='tight')

    return fig, ax


'''
Graafi komponentide (ülekattes olevate hulkade) kujutamine joondiagrammil.
Parameetrid:    df_original - graafi komponentide dataframe. 
                plot_params - joondiagrammi kujunduse atribuudid.
                subset - komponendi pikkus.
                figname - failinimi joonise salvestamiseks.
Väljund: graafiku joonis (fig) ja teljed (ax).
'''
def plot_components(df_original, plot_params, subset=None, figname=None):
    df = df_original.copy()
    fig, ax = draw_lineplot(plot_params)  # joonise tegemine (ilma väärtusteta)
    if subset is not None:
        df = df[df['cluster_size'] == subset]  # alamhulga võtmine (jätab alles vaid read etteantud komponendi pikkusega)

    # jätab alles y-telje väärtused (veerud 100, 200, 300, 358)
    df = df.drop(['Unnamed: 0', 'cs_id_100', 'cs_id_200', 'cs_id_300', 'cs_id_358', 'cs_id_966', 'cluster_size'], axis=1)

    for i in range(df.shape[0]):
        y = df.iloc[i]
        ax.plot([100, 200, 300, 358, 966], y, marker='o', ms=4, linewidth=1)

    # joonise salvestamine
    if figname is not None:
        fig.savefig(os.getcwd() + '/figures/' + figname)

    return fig, ax


'''
Tulemuste kujutamine joondiagrammil.
Parameetrid:    plot_params - joondiagrammi kujunduse atribuudid.
                x - järjend x-telje väärtustest.
                y - järjend y-telje väärtustest.
                figname - failinimi joonise salvestamiseks.
Väljund: graafiku joonis (fig) ja teljed (ax).
'''
def draw_lineplot(plot_params, x=None, y=None, annotation_coords=None, figname=None):
    fig, ax = create_plot(plot_params)

    if x is not None and y is not None:
        ax.plot(x, y, color=plot_params['linecolor'], linestyle='-', linewidth=plot_params['linewidth'], zorder=1)
        plt.scatter(x, y, s=plot_params['ms'], c=['#5975a4', '#cc8963', '#5f9e6e', '#b55d60', '#857aab'], zorder=2)

        if annotation_coords is not None:
            for i in range(len(x)):
                ax.text(x[i] + annotation_coords[0], y[i] + annotation_coords[1], str(int(y[i])),
                          fontsize=plot_params['fontsize'])#, color=plot_params['fontcolor'])

    # joonise salvestamine
    if figname is not None:
       fig.savefig(os.getcwd() + '/figures/' + figname)

    return fig, ax


'''
Graafi komponentides (ülekattes olevate hulkade) olevate hulkade suuruste kujutamine viiuldiagrammil.
Parameetrid:    df - graafi komponentide dataframe.
                plot_params - viiuldiagrammi kujunduse atribuudid.
                annotation_coords - järjend [x, y] annotatsioonide asukoha liigutamiseks punktide suhtes.
                figname - failinimi joonise salvestamiseks.
Väljund: graafiku joonis (fig) ja teljed (ax).
'''
def draw_violinplot(df, plot_params, annotation_coords=None, figname=None):
    columns = ['100', '200', '300', '358', '966']

    annotations = []
    for column in columns: # mediaanide annotatsioonide tegemine
        annotations.append(df[column].median())

    x = range(len(annotations))
    fig, axes = plt.subplots(figsize=plot_params['figsize'])

    plt.rcParams['font.size'] = plot_params['fontsize']
    plt.xticks(fontsize=plot_params['ticks_size'])
    plt.yticks(fontsize=plot_params['ticks_size'])

    for i in range(len(columns)):
        # annotatsioonide lisamine joonisele
        axes.text(x[i] + annotation_coords[0], annotations[i] + annotation_coords[1], str(int(annotations[i])),
                  fontsize=plot_params['fontsize'], color=plot_params['fontcolor'])

    ax = sns.violinplot(data=df, ax=axes)

    ax.set_xlabel(plot_params['x_label'], fontsize=plot_params['label_fontsize'], labelpad=plot_params['label_padding'])
    ax.set_ylabel(plot_params['y_label'], fontsize=plot_params['label_fontsize'], labelpad=plot_params['label_padding'])
    ax.margins(plot_params['margins'][0], plot_params['margins'][1])

    # joonise salvestamine
    if figname is not None:
        fig.savefig(os.getcwd() + '/figures/' + figname)

    return fig, ax
