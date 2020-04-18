import networkx as nx
import pandas as pd
import math
import matplotlib.pyplot as plt

# load patient csv data
patientData = pd.read_csv('PatientInfo.csv')

# create directed infection graph
g = nx.DiGraph()
for index, row in patientData.iterrows():
    if not math.isnan(row['infected_by']):
        g.add_edge(row['infected_by'], row['patient_id'])
        
# count nodes in graph
print(g.number_of_nodes())

# find root nodes and their subgraphs
for node in list(g):
    if (g.in_degree(node) == 0):
        print(node)
        subgraph = g.subgraph(nx.descendants(g, node)|{node})
        nx.draw_planar(subgraph)
        #plt.show()
        plt.savefig('subgraphs/' + str(node) + '.png')