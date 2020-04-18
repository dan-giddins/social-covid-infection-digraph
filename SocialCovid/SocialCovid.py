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
PROXIMITY_VALUE = 0.01
PROXIMITY_FOLDER = 'subgraphs_proximity'
PROXIMITY_PLOT = True
PROXIMITY_READ = False

def plot_proximity(proximityGraph, counter):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.axis('off')
    nx.draw_networkx(proximityGraph, node_size = 10, edge_color = '#aaaaaa', font_size = 1)
    plt.savefig(PROXIMITY_FOLDER + '/' + str(proximityGraph.number_of_nodes()) + '_proximity_' + str(counter) + '.png', dpi = 1000)
    plt.close()

def plot_infected(node, subg):
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
    plt.savefig(INFECTED_FOLDER + '/' + infected + "_" + rootNode + '.png', dpi = 300)
    plt.close()

def proximity(node1Locations, node2Locations):
    return geopy.distance.distance(node1Locations, node2Locations).km

def check_locations(locations, node1, node2, proximityGraph):
    for node1Locations in locations[node1]:
        for node2Locations in locations[node2]:
            if proximity(node1Locations, node2Locations) <= PROXIMITY_VALUE:
                proximityGraph.add_edge(node1, node2)
                print((node1, node2))
                return

def main():
    # create subgraph dirs
    if not os.path.exists(INFECTED_FOLDER):
        os.makedirs(INFECTED_FOLDER)
    if not os.path.exists(PROXIMITY_FOLDER):
        os.makedirs(PROXIMITY_FOLDER)

    # load patient csv data
    patientInfo = pd.read_csv('data/PatientInfo.csv')
    patientRoute = pd.read_csv('data/PatientRoute.csv')

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
                subg = infectionGraph.subgraph(nx.descendants(infectionGraph, node) | {node})
                if (INFECTED_PLOT):
                    plot_infected(node, subg)

    if (PROXIMITY_ENABLE):
        proximityGraph = None
        if (PROXIMITY_READ):
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
                                proximityGraph.add_edge(int(row1['patient_id']), int(row2['patient_id']))

            with open('proximityGraph', 'wb') as file:
                pickle.dump(proximityGraph, file)

        print(proximityGraph.number_of_edges())

        # find subgraphs
        proximityGraphCopy = proximityGraph.copy()
        counter = 1
        while (proximityGraphCopy.number_of_nodes() > 0):
            for node in list(proximityGraphCopy):
                print(node)
                tree = nx.dfs_tree(proximityGraphCopy, node)
                subgraph = proximityGraphCopy.subgraph(tree.nodes)
                if (PROXIMITY_PLOT):
                    plot_proximity(subgraph, counter)
                counter += 1
                proximityGraphCopy.remove_nodes_from(tree.nodes)
                break
        

if __name__ == "__main__":
    main()
