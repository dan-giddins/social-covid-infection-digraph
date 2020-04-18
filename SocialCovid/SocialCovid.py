import networkx as nx
import pandas as pd
import math
import matplotlib.pyplot as plt
from matplotlib import pylab
import os
import geopy.distance
import pickle


INFECTED_ENABLE = False
INFECTED_FOLDER = 'subgraphs_infected'
INFECTED_PLOT = False
PROXIMITY_ENABLE = True
PROXIMITY_FOLDER = 'subgraphs_proximity'
PROXIMITY_PLOT = True
PROXIMITY_READ = True

# plot proximity graph
def plot_proximity(proximityGraph, counter):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.axis('off')
    size = proximityGraph.number_of_nodes()
    # draw diffrent node densities diffrently
    if size > 100:
        node_size = 1
        font_size = 1
        dpi = 2000
        width = 0.1
    else:
        node_size = 100
        font_size = 6
        dpi = 300
        width = 1
        ax.set_xlim((-1.2, 1.2))
        ax.set_ylim((-1.2, 1.2))
    nx.draw_networkx(proximityGraph, node_size = node_size, width = width, edge_color = '#aaaaaa', font_size = font_size)
    plt.savefig(PROXIMITY_FOLDER + '/' + str(size) + '_proximity_' + str(counter) + '.png', dpi = dpi)
    plt.close()

# plot infected digraph
def plot_infected(node, subg):
    color_map = []
    for subnode in subg:
        if subnode == node:
            # colour root node red
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
    plt.savefig(INFECTED_FOLDER + '/' + infected + "_" + rootNode + '.png', dpi = 300)
    plt.close()

def main():
    # create subgraph dirs
    if not os.path.exists(INFECTED_FOLDER):
        os.makedirs(INFECTED_FOLDER)
    if not os.path.exists(PROXIMITY_FOLDER):
        os.makedirs(PROXIMITY_FOLDER)

    # load patient csv data
    patientInfo = pd.read_csv('data/PatientInfo.csv')
    patientRoute = pd.read_csv('data/PatientRoute.csv')

    # generate infection digraph 
    if (INFECTED_ENABLE):
        # create directed infection graph
        infectionGraph = nx.DiGraph()
        for index, row in patientInfo.iterrows():
            if not math.isnan(row['infected_by']):
                infectionGraph.add_edge(int(row['infected_by']), int(row['patient_id']))
        
        # count nodes in graph
        print(infectionGraph.number_of_nodes())

        # find root infectors and their subgraphs
        for node in list(infectionGraph):
            if (infectionGraph.in_degree(node) == 0):
                print(node)
                # include root infectors and their descendants
                subg = infectionGraph.subgraph(nx.descendants(infectionGraph, node) | {node})
                if (INFECTED_PLOT):
                    # plot
                    plot_infected(node, subg)
    
    # generate proximity graph 
    if (PROXIMITY_ENABLE):
        proximityGraph = None
        if (PROXIMITY_READ):
            # load graph from file
            with open('proximityGraph', 'rb') as file:
                proximityGraph = pickle.load(file)
        else:
            # create proximity graph
            proximityGraph = nx.Graph()
            proximityGrouping = patientRoute.groupby(['latitude', 'longitude'])
            for name, group in proximityGrouping:
                if (len(group) > 1):
                    for index1, row1 in group.iterrows():
                        for index2, row2 in group.iterrows():
                            if int(row1['patient_id']) != int(row2['patient_id']):
                                # add edge between two diffrent patients who have been at the same location
                                proximityGraph.add_edge(int(row1['patient_id']), int(row2['patient_id']))
            # write to file
            with open('proximityGraph', 'wb') as file:
                pickle.dump(proximityGraph, file)

        print(proximityGraph.number_of_edges())

        # find proximity subgraphs
        proximityGraphTemp = proximityGraph.copy()
        counter = 1
        # process all nodes in graph
        while (proximityGraphTemp.number_of_nodes() > 0):
            # get a node
            for node in list(proximityGraphTemp):
                print(node)
                # find all nodes connected to the given node
                tree = nx.dfs_tree(proximityGraphTemp, node)
                subgraph = proximityGraphTemp.subgraph(tree.nodes)
                # plot these nodes
                if (PROXIMITY_PLOT):
                    plot_proximity(subgraph, counter)
                counter += 1
                # remove these nodes from the temporary tree
                proximityGraphTemp.remove_nodes_from(tree.nodes)
                break
        

if __name__ == "__main__":
    main()
