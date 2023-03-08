# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 08:18:15 2023

@author: cstan
"""

import pandas as pd
import janitor
import datetime

from IPython.display import display, HTML
from pyvis import network as net
import networkx as nx
try:
    df_ori = pd.read_csv("C://users/cstan/Documents/CooperStandard/tutorials/graphs/Connections.csv", skiprows=2)
except Exception as e:
    print(f"Error opening file {e}\n")
print(df_ori.info())

df = (
    df_ori
    .clean_names() # remove spacing and capitalization
    .drop(columns=['first_name', 'last_name', 'email_address']) # drop for privacy
    .dropna(subset=['company', 'position']) # drop missing values in company and position
    .to_datetime('connected_on', format='%d %b %Y')
  )
print(df.head())

'''
If you’re not familiar with the syntax above, what it’s doing is chaining operations one after the other.

For example, df_ori.clean_names().drop(...) means you’re cleaning the column names, then dropping the columns, and 
so on, where the output of the first operation becomes the input of the next.

This approach is called functional programming, and I personally like it because it’s clean and simple.

What we basically did above is cleaning the column names, dropping columns, removing missing values, and converting 
the date column to DateTime format, all in one block!

Now that our data is in a good shape, let’s do some exploratory data analysis.
'''
'''
What I’m doing here is getting the value count of the company column, which acts like a counter for 
every company, take only the top 10, and then plotting a bar chart. I also inverted the y-axis so that the names are easier to read.
'''
df['company'].value_counts().head(10).plot(kind="barh").invert_yaxis();

pattern = "freelance|self-employed"
df = df[~df['company'].str.contains(pattern, case=False)]

'''
Using value_counts()again, along with sort_values(), we’re able to get a new dataframe of the companies along with the counts.

We do the same process for the position column.

Now we have our data frame, it’s time to create our network.

'''
df['connected_on'].hist(xrot=35, bins=15)

df_company = df['company'].value_counts().reset_index()
df_company.columns = ['company', 'count']
df_company = df_company.sort_values(by="count", ascending=False)
print(df_company.head(10))

df_position = df['position'].value_counts().reset_index()
df_position.columns = ['position', 'count']
df_position = df_position.sort_values(by="count", ascending=False)
print(df_position.head(10))

#Before we create our LinkedIn network, let’s start small, and figure out how PyVis and networkX work.
'''
First things first, we create our network class which takes in a graph object in the end, and then save the network as an HTML.

To form our graph, we construct it with the Graph class, and then add nodes to it. The add_node function takes in a couple of arguments.

The numbers you see at the start are unique id’s, this allows us to connect them later on. You can also use the labels as ID’s as long as they are unique.

You can control the size by assigning integer values to the argument, and the title argument stands for the hover info.
'''

nt = net.Network(notebook=True)

g = nx.Graph()
g.add_node(0, label = "root") # intialize yourself as central node
g.add_node(1, label = "Company 1", size=10, title="info1")
g.add_node(2, label = "Company 2", size=40, title="info2")
g.add_node(3, label = "Company 3", size=60, title="info3")
g.add_edge(0, 1)
g.add_edge(0, 2)
g.add_edge(0, 3)

nt.from_nx(g)
nt.show('nodes.html')
display(HTML('nodes.html'))

print(f"number of nodes: {g.number_of_nodes()}")
print(f"number of edges: {g.number_of_edges()}")

for _, row in df_company.head(5).iterrows():
  print(row['company'] + "-" + str(row['count']))
  
print(df_company.shape)
df_company_reduced = df_company.loc[df_company['count']>=5]
print(df_company_reduced.shape)


print(df_position.shape)
df_position_reduced = df_position.loc[df_position['count']>=5]
print(df_position_reduced.shape)
'''
First you initialize the graph, and add the root node, which is yourself.

Then we use iterrows() , which basically allows us to iterate the rows of our dataframe.

In each for loop, we save the company name and count for use later.

We want each of the nodes to display the positions that our connection holds at those companies, so to achieve that, we use a list comprehension to grab the positions and store them in a set (to prevent duplication).

To make the hover information on our nodes prettier, we use HTML to format our information.

At the end of each loop, we add the new node, and then add a link our root node.

After our graph is done building, we add it to the network, and we can display it.
'''

# initialize graph
g = nx.Graph()
g.add_node('root') # intialize yourself as central

# use iterrows tp iterate through the data frame
for _, row in df_company_reduced.iterrows():

  # store company name and count
  company = row['company']
  count = row['count']

  title = f"{company} – {count}"
  positions = set([x for x in df[company == df['company']]['position']])
  positions = ''.join('{}'.format(x) for x in positions)

  position_list = f"{positions}"
  hover_info = title + position_list

  g.add_node(company, size=count*2, title=hover_info, color='#3449eb')
  g.add_edge('root', company, color='grey')

# generate the graph
nt = net.Network(height='700px', width='700px', bgcolor="black", font_color='white')
nt.from_nx(g)
nt.hrepulsion()
# more customization https://tinyurl.com/yf5lvvdm
nt.show('company_graph.html')
display(HTML('company_graph.html'))

# initialize graph
g = nx.Graph()
g.add_node('root') # intialize yourself as central

# use iterrows tp iterate through the data frame
for _, row in df_position_reduced.iterrows():

  count = f"{row['count']}"
  position= row['position']
  
  g.add_node(position, size=count, color='#3449eb', title=count)
  g.add_edge('root', position, color='grey')

# generate the graph
nt = net.Network(height='700px', width='700px', bgcolor="black", font_color='white')
nt.from_nx(g)
nt.hrepulsion()
# more customization https://tinyurl.com/yf5lvvdm
nt.show('position_graph.html')
display(HTML('position_graph.html'))
