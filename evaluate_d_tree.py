import sys
import math
from learn_d_tree import *

###### evaluate_d_tree.py
#      This file will load a decision tree and a dataset from a given file.
#      It will evaluate the decision tree's classification accuracy on the dataset
######

def evaluate_tree_on_data(tree, data):
    """Test and print out how this tree performs on this data"""
    absolute_error = 0.0
    for d in data:
        win_prob = tree.get_prob_of_win(d.features)
        prediction = 0
        if win_prob > 0.5:
            prediction  = 1
        error = math.fabs(prediction - d.label)
        absolute_error += error
    
    #Display results to screen
    print('Decision tree evaluated on ', len(data), ' data instances')
    print('   Total Absolute Error   : ', absolute_error)
    print('   Average Absolute Error : ', absolute_error / len(data))
    
if __name__ == "__main__":
    #Get ais from command line arguments
    if len(sys.argv) != 3:
        print('Usage: evaluate_d_tree.py d_tree_file.tree data_file.dat')
        sys.exit()

    #get d tree file name
    treefilename = sys.argv[1]
    
    #get data file name
    datafilename = sys.argv[2]
        
    #Open the datafile
    datafile = open(datafilename, 'r')    
    
    #Read/Load the data from the file
    data = read_data(datafile)
    
    #Close the datafile
    datafile.close()
    
    #Load the Decision Tree
    tree = loadDTree(treefilename)
    
    #Evaluate tree
    evaluate_tree_on_data(tree,data)