# -*- coding: utf-8 -*-
script_name = 'gurobi_Original'

"""
Main script for the two-stage SP model
"""

# import statements
import pandas as pd
import numpy as np
from gurobipy import *
from plugins import *
import time
import config  # Importing the parameters and data reading method from config.py

tic = time.perf_counter()
print('define set ...\n')

# Unpack parameters from config
IS = config.IS
AS = config.AS
LS = config.LS
NS = config.NS

print('define parameters ...\n')

# Read data using the method from config.py
CF, U, H, V, CP, CH, G, CT, D, pr, demand = read_data()


# create a new model
m = Model("two-stage_SP")

# create sets
IS = range(IS)
AS = range(AS)
LS = range(LS)
NS = range(NS)

# create variables
print('define variables ...\n')
x = m.addVars(IS,LS,vtype=GRB.BINARY, name="x")
y = m.addVars(AS,IS,vtype=GRB.INTEGER, name="y")
q = m.addVars(NS,AS,IS,IS,vtype=GRB.INTEGER, name="q")   
z = m.addVars(NS,AS,IS,vtype=GRB.INTEGER, name="z")
w = m.addVars(NS,AS,IS,vtype=GRB.INTEGER, name="w")
hc = m.addVars(NS,vtype=GRB.CONTINUOUS, name="hc")
tc = m.addVars(NS,vtype=GRB.CONTINUOUS, name="tc")
wc = m.addVars(NS,vtype=GRB.CONTINUOUS, name="wc")

# Non-negativity constraints
m.addConstrs((y[a,i] >= 0 for a in AS for i in IS), "y non-negative")
m.addConstrs((q[s,a,i,j] >= 0 for s in NS for a in AS for i in IS for j in IS), "q non-negative")
m.addConstrs((z[s,a,i] >= 0 for s in NS for a in AS for i in IS), "z non-negative")
m.addConstrs((w[s,a,j] >= 0 for s in NS for a in AS for j in IS), "w non-negative")

f = m.addVar(vtype=GRB.CONTINUOUS,name='f')
fc = m.addVar(vtype=GRB.CONTINUOUS,name='fc')
pc = m.addVar(vtype=GRB.CONTINUOUS,name='pc')

# Non-negativity constraints
m.addConstr((f >= 0),"f non-negative")
m.addConstr((fc >= 0),"fc non-negative")
m.addConstr((pc >= 0),"pc non-negative")
m.addConstrs((hc[s] >= 0 for s in NS),"hc non-negative")
m.addConstrs((tc[s] >= 0 for s in NS),"tc non-negative")
m.addConstrs((wc[s] >= 0 for s in NS),"wc non-negative")

print('define Constraint (2) ...\n')
m.addConstrs((sum(y[a,i] * V[a] for a in AS) <= sum(x[i,l] * U[l] for l in LS) for i in IS), 
             "Constraint (2)")

print('define Constraint (3) ...\n')
m.addConstrs((z[s,a,i] == y[a,i] - sum(q[s,a,i,j] for j in IS) for a in AS for i in IS for s in NS), 
              "Constraint (3)")

print('define Constraint (4) ...\n')
# C03
m.addConstrs((w[s,a,j] == D[s,a,j] - sum(q[s,a,i,j] for i in IS) for a in AS for j in IS for s in NS), 
             "Constraint (4)")

print('define Constraint (5) ...\n')
# C04
m.addConstrs((sum(x[i,l] for l in LS) <= 1 for i in IS), "Constraint (5)")


print('objective functions')
# C05
m.addConstrs((wc[s] == sum(G[a] * w[s,a,j] 
                           for a in AS for j in IS) for s in NS), "Shortage Costs")
    
m.addConstrs((hc[s] == sum(CH[a] * z[s,a,i] 
                           for a in AS for i in IS) for s in NS), "Surplus Costs")

m.addConstrs((tc[s] == sum(CT[a] * H[i,j] * q[s,a,i,j] 
                           for a in AS for i in IS for j in IS) for s in NS), "Transportation Costs")

print('define objective ...\n')

# Objective
m.addConstr((fc == sum(CF[l] * x[i,l] for i in IS for l in LS)), "Fixed Facility Costs")

m.addConstr((pc == sum(CP[a] * y[a,i] for a in AS for i in IS)), "Procurement Costs")

m.addConstr((f == fc + pc + sum(pr[s] * (tc[s] + hc[s] + wc[s]) for s in NS)), "Objective Function")

m.setObjective((f), GRB.MINIMIZE)

#output result within given time
m.setParam('TimeLimit', 3600)

print('solving ...\n')

m.optimize()

print('solved!')

# Work in progress
if m.status == GRB.OPTIMAL:

    Vx = np.zeros((IS[-1]+1,LS[-1]+1))
    Vy = np.zeros((AS[-1]+1,IS[-1]+1))
    Vq = np.zeros((NS[-1]+1,AS[-1]+1,IS[-1]+1,IS[-1]+1))
    Vz = np.zeros((NS[-1]+1,AS[-1]+1,IS[-1]+1))
    Vw = np.zeros((NS[-1]+1,AS[-1]+1,IS[-1]+1))
    #Vtc = np.zeros((NS[-1]+1,1))
    #Vhc = np.zeros((NS[-1]+1,1))
    #Vwc = np.zeros((NS[-1]+1,1))
    for i in IS:
        for l in LS:
            Vx[i,l] = x[(i,l)].x
        for a in AS:
            Vy[a,i] = y[(a,i)].x
            for s in NS:
                for j in IS:
                    Vq[s,a,i,j] = q[(s,a,i,j)].x
                Vz[s,a,i] = z[(s,a,i)].x
                Vw[s,a,i] = w[(s,a,i)].x
                #Vtc[s,1] = tc[s].x
                #Vhc[s,1] = w[s].x
                #Vwc[s,1] = w[s].x
    Vfc = fc.x
    Vpc = pc.x
    Vtc = sum(pr[s] * tc[s].x for s in NS)
    Vhc = sum(pr[s] * hc[s].x for s in NS)
    Vwc = sum(pr[s] * wc[s].x for s in NS)        
    Vf = m.getObjective().getValue()
    costs = pd.DataFrame([Vf,Vfc,Vpc,Vtc,Vhc,Vwc]).T
    location = pd.DataFrame(Vx)
    inventory = pd.DataFrame(Vy).T
    
    toc = time.perf_counter()
    elapsed_time = toc - tic

    save_and_print_results(script_name, config.IS, config.NS, config.MS, config.SS_SAA, opt_f, elapsed_time)

    # save_detailed_results(
    #     filename='data.xlsx',  # The target Excel file
    #     script_name=script_name,               # The script/method name used for the computation
    #     Vx=Vx,                                # The location data
    #     Vy=Vy,                                # The inventory data
    #     elapsed_time=elapsed_time,            # The elapsed time of the computation
    #     start_row=1,                          # The starting row in the Excel sheet
    #     sheet_name='result'         # The sheet name in the Excel file
    # )

else:
    print('Hmm, something went wrong!')
