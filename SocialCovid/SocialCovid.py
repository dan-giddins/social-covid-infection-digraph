import networkx as nx
import pandas as pd
import math
import matplotlib.pyplot as plt
from matplotlib import pylab
import os

def main():
    # load patient csv data
    patientInfo = pd.read_csv('data/PatientInfo.csv')
    patientRoute = pd.read_csv('data/PatientRoute.csv')

    # create directed infection graph
    g = nx.DiGraph()
    for index, row in patientInfo.iterrows():
        if not math.isnan(row['infected_by']):
            g.add_edge(int(row['infected_by']), int(row['patient_id']))
        
    # count nodes in graph
    print(g.number_of_nodes())

    # create subgraph dir
    if not os.path.exists('subgraphs'):
        os.makedirs('subgraphs')

    # find root nodes and their subgraphs
    for node in list(g):
        if (g.in_degree(node) == 0):
            print(node)
            subg = g.subgraph(nx.descendants(g, node)|{node})
            color_map = []
            for subnode in subg:
                if subnode == node:
                    color_map.append('#ffaaaa')
                else: 
                    color_map.append('#aaaaff')
            fig = plt.figure()
            ax = fig.add_subplot(111)
            rootNode = str(node)
            fig.suptitle('Infection source: ' + rootNode)
            infected = str(subg.number_of_nodes() - 1)
            ax.set_title('Total infected: ' + infected)
            ax.axis('off')
            nx.draw_networkx(subg, node_size = 100, node_color = color_map, edge_color = '#aaaaaa', font_size = 6)
            #plt.show()
            plt.savefig('subgraphs/'+ infected + "_" + rootNode + '.png', dpi = 300)
            plt.close()


if __name__ == "__main__":
    main()
