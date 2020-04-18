import networkx as nx
import pandas as pd
import math
import matplotlib.pyplot as plt
from matplotlib import pylab
import os

def main():
    # load patient csv data
    patientData = pd.read_csv('PatientInfo.csv')

    # create directed infection graph
    g = nx.DiGraph()
    for index, row in patientData.iterrows():
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
            fig.suptitle('Infection source: ' + str(node))
            ax = fig.add_subplot(111)
            ax.set_title('Total infected: ' + str(subg.number_of_nodes() - 1))
            ax.axis('off')
            nx.draw_networkx(subg, node_size = 100, node_color = color_map, edge_color = '#aaaaaa', font_size = 6)
            #plt.show()
            plt.savefig('subgraphs/'+ str(subg.number_of_nodes()) + "_" + str(node) + '.png', dpi = 300)
            plt.close()


if __name__ == "__main__":
    main()
