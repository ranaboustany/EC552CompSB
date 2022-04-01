#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 11:09:33 2022

@author: ranaboustany
"""

# import modules
import math
import csv
import pandas as pd
import time

# GATE class blueprint for gate creation 
class Gate:
    def __init__(self, name, ymax, ymin, n, k, type):
        self.name = name
        self.ymax = ymax
        self.ymin = ymin
        self.k = k
        self.n = n
        self.type = type
        
        if type == 'AND':
            self.truth = [0,0,0,1]
        elif type == 'OR':
            self.truth = [0,1,1,1]
        elif type == 'XOR':
            self.truth = [0,1,1,0]
        elif type == 'NAND':
            self.truth = [1,1,1,0]
        elif type == 'NOR':
            self.truth = [1,0,0,0]
        elif type == 'XNOR':
            self.truth = [1,0,0,1]
            
        self.out = [] # out would be the list of ys calculated for intermediate gates
        
    def stretch(self, x):
        if x>1.5:
            print("x can be at most 1.5\nPlease try again")
        else:
            self.ymax *= x 
            self.ymin /= x
            print('Your selected gate:', self.name, 'has been stretched!')
     
    def increase_slope(self, x):
        if x>1.5:
            print("x can be at most 1.05\nPlease try again") 
        else:
            self.n *= x
            print('Increase slope successful for gate:', self.name)
        
    def decrease_slope(self, x):
        if x>1.5:
            print("x can be at most 1.05\nPlease try again")  
        else:
            self.n /= x
            print('Decrease slope successful for gate:', self.name)
        
    def stronger_promoter(self, x):
        self.ymax *= x
        self.ymin *= x
        print('Stronger promoter successful for gate:', self.name)

    def weaker_promoter(self, x):
        self.ymax /= x
        self.ymin /= x
        print('Weaker promoter successful for gate:', self.name)       
       
    def stronger_RBS(self, x):
        self.k /= x
        print('Stronger RBS successful for gate:', self.name) 

    def weaker_RBS(self, x):
        self.k *= x
        print('Weaker RBS successful for gate:', self.name)
    

# Input signal Class
class Signal:
    def __init__(self, name, low, high):
        self.name = name
        self.low = low
        self.high = high
        
class Circuit:
    def __init__(self, name, design_df):
        self.name = name
        self.design = design_df
        self.score = None #declare empty variable
            
def computeXs(l1, h1, l2, h2):
    ### FOR A GATE THAT TAKES IN 2 INPUTS: computes Xs for the gate. returns x1, x2, x3, x4.
    x1_LL = l1+l2 # x1 adds low values of inputs
    x2_HL = h1+l2 # x2 adds high of first input and low of second input
    x3_LH = l1+h2 # x3 adds low of first input and high of second input
    x4_HH = h1+h2 # x4 adds high values of inputs
    
    return x1_LL, x2_HL, x3_LH, x4_HH

def computeYs(x1, x2, x3, x4, gate):
    ### FOR A GATE THAT TAKES IN 2 INPUTS: computes Ys
    y1 = gate.ymin + (gate.ymax - gate.ymin)/(1.0+(x1/gate.k)**gate.n)
    y2 = gate.ymin + (gate.ymax - gate.ymin)/(1.0+(x2/gate.k)**gate.n)
    y3 = gate.ymin + (gate.ymax - gate.ymin)/(1.0+(x3/gate.k)**gate.n)
    y4 = gate.ymin + (gate.ymax - gate.ymin)/(1.0+(x4/gate.k)**gate.n)
    
    Ys = [y1, y2, y3, y4]
    gate.out = Ys
    
    return Ys
    
def score(gate, Ys):
    truth = gate.truth
    
    lowestON = 999999999
    highestOFF = 0
    for i in range(len(truth)): 
        if truth[i] == 1:
            if Ys[i] < lowestON:
                lowestON = Ys[i]
        if truth[i] == 0:
            if Ys[i] > highestOFF:
                highestOFF = Ys[i]
    
    score = math.log((lowestON/highestOFF), 10)
    
    return score

def computeAvg(gate, Ys):
    ### FOR INTERMEDIATE GATES: Takes in gate and its correponding Ys as list
    ### then Computes and returns the average Low and average High of gate 
    truth = gate.truth
    countL = 0
    sumL = 0
    countH = 0
    sumH = 0
    for i in range(len(truth)):
        if truth[i] == 0:
            countL += 1
            sumL+= Ys[i]
        elif truth[i] == 1:
            countH += 1
            sumH += Ys[i]
    avgL = sumL/countL
    avgH = sumH/countH
    
    return avgL, avgH
            
            
def connect(part1, part2, part3):
    ### connects part 1 and part 2 to part 3. Parts 1&2 can be gates or signals but part 3 must be a gate.
    if type(part3) != Gate:
        print("ERROR: your third part needs to be a Gate")
    else:
        if type(part1) == Gate: #if part 1 is a gate then  it must be an interrmediate gate based on the restrictions of the program so it would have Ys
            [L1, H1] = computeAvg(part1, part1.out)
        else:    
            L1 = part1.low
            H1 = part1.high
        if type(part2) == Gate:
            [L2, H2] = computeAvg(part2, part2.out)
        #elif type(part2) == Gate:
        else:
            L2 = part2.low
            H2 = part2.high
            
        
        x1, x2, x3, x4 = computeXs(L1,H1,L2,H2)
        
        y1, y2, y3, y4 = computeYs(x1, x2, x3, x4, part3)
        
        print(part1.name, 'and', part2.name, "are connected to", part3.name)
        
def was_gate_used(gate_name, gates_used_list):
    ### Checks if a gate name is in a list of gates (of gate classes)
    gates_used_names = []
    for gate in gates_used_list:
        name = gate.name
        gates_used_names += [name]
    if gate_name in gates_used_names:
        return True
    else:
        return False
        
def read_design(design, gates, signals):
    ### this function takes in 3 pandas dataframes: the first containing the order of the parts, the second is the gate library and 3rd is the signal library, 
    ### Function then outputs the score of the circuit
    global gates_used
    global list_gates 
    global list_signals
    
    for i in range(len(design)):
        in1 = design.at[i,'IN1']
        in2 = design.at[i,'IN2']
        gate = design.at[i,'GATE']
        
        # now that we have the names of the parts, we need to convert them into their appropriate class
        
        # PART 1: input 1
        if (in1 not in list_gates) and (in1 not in list_signals):
            print("ERROR: part 1 is not a gate or a signal ")
            break
        elif in1 in list_gates:
            if was_gate_used(in1, gates_used):
                for g in gates_used:
                    if g.name == in1:
                        in1_class = g
                        break
            else:
                in1_class = Gate(in1, gates.at[in1, 'ymax'], gates.at[in1, 'ymin'], gates.at[in1, 'n'], gates.at[in1, 'k'], gates.at[in1, 'Type'])
        else: #else it's an input signal
            in1_class = Signal(in1, signals.at[in1, 'Low'], signals.at[in1, 'High'])
          
        # PART 2: input 2
        if (in2 not in list_gates) and (in2 not in list_signals):
            print("ERROR: part 2 is not a gate or a signal ")
            break
        elif in2 in list_gates:
            if was_gate_used(in2, gates_used):
                for g in gates_used:
                    if g.name == in2:
                        in2_class = g
                        break
            else:
                in2_class = Gate(in2, gates.at[in1, 'ymax'], gates.at[in2, 'ymin'], gates.at[in2, 'n'], gates.at[in2, 'k'], gates.at[in2, 'Type'])
        else: #else it's an input signal
            in2_class = Signal(in2, signals.at[in2, 'Low'], signals.at[in2, 'High'])
            
        # PART 3: Gate
        if (gate not in list_gates):
            print('ERROR: part 3 is not a gate ', i)
            break
        else:
            gate_class = Gate(gate, gates.at[gate, 'ymax'], gates.at[gate, 'ymin'], gates.at[gate, 'n'], gates.at[gate, 'k'], gates.at[gate, 'Type'])
            
        #print("we wanna connect:", in1_class.name, 'and', in2_class.name, 'to', gate_class.name)    
            
        connect(in1_class, in2_class, gate_class)
        
        gates_used = [gate_class] + gates_used
        
        
        # COULD ADD SCORE CALCULATION AT EACH GATE HERE + STORE IT
        
        if i == (len(design)-1):
            final_score = score(gate_class, gate_class.out)
            return final_score
    

def design():
    global gates_used
    gates_used = []
    with open('design.csv','w+') as file:
        myFile = csv.writer(file)
        myFile.writerow(["IN1","IN2","GATE"])
        noOfConnections = int(input("Please enter how many connections you would like to make (INTEGER): "))
        for con in range(noOfConnections):
            IN1 = input("Please enter your first input: ")
            IN2 = input("Please enter your second input: ")
            GATE = input("Please enter your gate: ")
        
            IN1 = IN1.upper()
            IN2 = IN2.upper()
            GATE = GATE.upper()
            
            print("\nConnection", str(con+1), ":", IN1, "and", IN2, "will connect to", GATE )
            myFile.writerow([IN1, IN2, GATE])
        print("\nDesign completed!")
        
        
def designRules():
    print("\nFor your circuit design, you can pick your Gates and Input Signals from the libraries.")
    time.sleep(5)
    print("\nYou will have the option to choose an action from a menu... but before that, please go over the following rules:")
    time.sleep(5)
    print('''
          1 - You can only build forward
          
          2 - Gates must have 2 inputs and will only have 1 output
          
          3 - To respect the design restictions above, you will be prompted to connect 2 parts to a gate at once
              for example: input1, input2, gate
                           Meaning that input1 and input2 are connected to the gate
          
          4 - When designing a circuit, you will be first asked to enter how many total connections you wish to have in your circuit
              Connecting input1 and input2 to a gate counts as ONE connection
              
          5 - When prompted to input your parts, note that:
                  
                  - Input1 & Input2 can be gates or signals
                    HOWEVER, a gate can only be used as an input if it has already been used before.
                
                  - Part 3 MUST be a gate
                  
              We strongly recommend you draw out your ciircuit before typing in the connections.
          
          6 - You can modify a gate in the library of gates by applying the following operations:
                  Stretch, Increase slope, Decrease slope, Stronger promoter, Weaker promoter, Stronger RBS, Weaker RBS
            
            If you do so, you will no longer be able to see your original gate as changes will be directly done to the library
            
            If you choose to modify your gate(s), you must make the modification, then reinput the whole circuit design.
    ''')
    
def modifyGates():
    global gate_lib
    print("Here is your library of gates:")
    print(gate_lib)
    print("What gate would you like to modify?")
    gate = input("Enter gate name: ")
    gate = gate.upper() 
    gate_class = Gate(gate, gate_lib.at[gate,'ymax'], gate_lib.at[gate,'ymin'], gate_lib.at[gate,'n'], gate_lib.at[gate,'k'], gate_lib.at[gate,'Type'])
    
    print('''What modification would you like to make?
              a. Stretch
              b. Increase slope
              c. Decrease slope
              d. Stronger promoter
              e. Weaker promoter
              f. Stronger RBS
              g. Weaker RBS
          ''')
    modi = input("Enter modification a,b,c,d,e,f,or g: ")
    
    if modi == "a":
        x = float(input("Enter value to stretch by (max is 1.5): "))
        gate_class.stretch(x)
    elif modi == "b":
        x = float(input("Enter value to increase slope by (max is 1.5): "))
        gate_class.increase_slope(x)   
    elif modi == "c":
        x = float(input("Enter value to decrease slope by (max is 1.5): "))
        gate_class.decrease_slope(x)
    elif modi == "d":
        x = float(input("Enter value to strengthen promoter by: "))
        gate_class.stronger_promoter(x)
    elif modi == "e":
        x = float(input("Enter value to weaken promoter by: "))
        gate_class.weaker_promoter(x)
    elif modi == "f":
        x = float(input("Enter value to strengthen RBS by: "))
        gate_class.stronger_RBS(x)
    elif modi == "g":
        x = float(input("Enter value to weaken RBS by: "))
        gate_class.weaker_RBS(x)
    else:
        print('Try again')
        modifyGates()
        
    # save modified gate in library
    
    gate_lib.at[gate_class.name, 'ymax'] = gate_class.ymax
    gate_lib.at[gate_class.name, 'ymin'] = gate_class.ymin
    gate_lib.at[gate_class.name, 'n'] = gate_class.n
    gate_lib.at[gate_class.name, 'k'] = gate_class.k

    return gate_lib

def showTruthTable():
    gate = input("Enter gate name: ")
    gate = gate.upper() 
    gate_class = Gate(gate, gate_lib.at[gate,'ymax'], gate_lib.at[gate,'ymin'], gate_lib.at[gate,'n'], gate_lib.at[gate,'k'], gate_lib.at[gate,'Type'])
    print('The truth table for gate', gate, 'is:')
    print(gate_class.truth)
    print("It's an", gate_class.type, 'gate!')
    
def saveHistory(circuits, scores):
    ### Takes in 2 lists: circuit names and list of scores for each circuit and creates a csv file
    with open('history.csv','w+') as file:
        myFile = csv.writer(file)
        myFile.writerow(["Circuit","Score"])
        for i in range(len(scores)):
            c = circuits[i].name
            s = (scores[i])
            myFile.writerow([c, s])
        
            
# def showGraph(filename):
#     ###  Takes in file name and prints out graph of result history
#     hist = pd.read_csv(filename, header=0)
    
    
    
    
        
gate_lib = pd.read_csv('gateLibrary.csv', header=0)
gate_lib = gate_lib.set_index('Gate')
list_gates = gate_lib.index.values.tolist() #NEED THIS GLOBAL VARIABLE
# Import input signal library as pandas dataframe
input_signal = pd.read_csv('inputSignalLibrary.csv', header=0)
input_signal = input_signal.set_index('Input ')
list_signals = input_signal.index.values.tolist() #NEED THIS GLOBAL VARIABLE
    
gates_used = []


def main():
    print("\nWELCOME!!!\n\nLet's design a genetic circuit!\n")
    time.sleep(2)
    print("Importing libraries...")
    # Import gate library as pandas dataframe
    global gate_lib
    global list_gates
    global input_signal
    global list_signals
    global gates_used
    
    time.sleep(2)
    print('\nImport successful! Here are your libraries of Gates and Input Signals:\n')
    time.sleep(2)
    print(gate_lib)
    time.sleep(2)
    print('\n')
    print(input_signal)
    
    designRules()
    
    actions = [] #variable keeps track of actions: list of actions
    circuits = [] #variable keeps track of designed circuits: list of names
    scores = [] #variable keeps track of scores of designed circuits: list of scores
    designCount = 0
    scoreCount = 0
    
    launch = True
    
    time.sleep(10)
    print("LET'S GET STARTED!")
    time.sleep(2)
    while launch:
        time.sleep(2)
        print("\nWhat would you like to do?")
        print('''
          a - Show gate library
          b - Show input signal library
          c - Show design rules
          d - Design circuit
          e - Show circuit connections
          f - Modify gates
          g - Show truth table
          h - Calculate circuit score 
          i - Results
          j - Exit program
          ''')
        time.sleep(1)
        action = input("Please enter action letter: ")
        
    
        if action == 'a':
            time.sleep(0.50)
            #gate_lib = gate_lib
            print(gate_lib)
        elif action == 'b':
            time.sleep(0.50)
            print(input_signal)
        elif action == 'c':
            designRules()
        elif action == 'd':
            design()
            designCount += 1
            design_df = pd.read_csv('design.csv', header=0)
            # create circuit class
            circuitName = "circuit" + str(designCount)
            circuit_class = Circuit(circuitName, design_df)
            circuits += [circuit_class]
            print("\nNow calculate the score of your design!\nPICK h AS YOUR NEXT ACTION!")
        elif action == 'e':
            if 'd' not in actions:
                print("\nYou must design your circuit first.")
            else:
                print(design_df)
        elif action == 'f':
            new_gate_lib = modifyGates()
            gate_lib = new_gate_lib
            print("Successful modification. Please recreate circuit design before calculating score (use action d).")
        elif action == 'g':
            showTruthTable()
        elif action == 'h':
            if 'd' not in actions:
                print("\nYou must design your circuit first.")
            else:
                score = read_design(design_df, gate_lib, input_signal)
                circuit_class.score = score
                scoreCount += 1
                if scoreCount == designCount:
                    scores += [float(score)]
                    print("The final score for this circuit is =", score)
                else:
                    print("Please recreate circuit design before calculating score (use action d)")
                    scoreCount -= 1
                
        elif action == 'i':
            saveHistory(circuits, scores)
            
            history_df = pd.read_csv('history.csv', header=0)
            history_df  = history_df.set_index('Circuit')
            
            print("Here is your result summary:")
            print(history_df)
            
            print("These results can be found in the 'history' file found in your working directory.")
            #showGraph('history.csv')
            
            tmp = max(scores) # find max score
            index = scores.index(tmp)
            bestCircuit = circuits[index]
            
            print("The highest score is:", tmp, "which corresponds to", bestCircuit.name, "which had the following design:", bestCircuit.design)
            
            
        elif action == 'j':
            launch = False
        else:
            print('Try again')
            
        actions += [action]
        


if __name__ == "__main__":
    main()

