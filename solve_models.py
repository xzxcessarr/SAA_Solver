# -*- coding: utf-8 -*-
"""
def getsol is for sample problem,
def renew is for original problem or large size problem (scenario number is 
larger); x and y are as input

"""
from gurobipy import Model, GRB, GurobiError
import numpy as np

max_attempts = 3

def getsol(IS,AS,LS,SS,CF,U,V,H,CP,CH,G,CT,D_sample,pr_sample):
    """
    尝试解决优化模型，如果在优化过程中出现异常，将重试最多 max_attempts 次。
    """
    attempt = 0
    while attempt < max_attempts:
        try:
            # 创建新模型
            m = Model("getsol")
                
            # create sets
            IS = range(IS)
            AS = range(AS)
            LS = range(LS)
            SS = range(SS)
            
            # create variables
            print('define variables ...\n')
            x = m.addVars(IS,LS,vtype=GRB.BINARY, name="x")
            y = m.addVars(AS,IS,vtype=GRB.INTEGER, name="y")
            q = m.addVars(SS,AS,IS,IS,vtype=GRB.INTEGER, name="q")   
            z = m.addVars(SS,AS,IS,vtype=GRB.INTEGER, name="z")
            w = m.addVars(SS,AS,IS,vtype=GRB.INTEGER, name="w")
            hc = m.addVars(SS,vtype=GRB.CONTINUOUS, name="hc")
            tc = m.addVars(SS,vtype=GRB.CONTINUOUS, name="tc")
            wc = m.addVars(SS,vtype=GRB.CONTINUOUS, name="wc")
            
            # Non-negativity constraints
            m.addConstrs((y[a,i] >= 0 for a in AS for i in IS), "y non-negative")
            m.addConstrs((q[s,a,i,j] >= 0 for s in SS for a in AS for i in IS for j in IS), "q non-negative")
            m.addConstrs((z[s,a,i] >= 0 for s in SS for a in AS for i in IS), "z non-negative")
            m.addConstrs((w[s,a,j] >= 0 for s in SS for a in AS for j in IS), "w non-negative")
            
            f = m.addVar(vtype=GRB.CONTINUOUS,name='f')
            fc = m.addVar(vtype=GRB.CONTINUOUS,name='fc')
            pc = m.addVar(vtype=GRB.CONTINUOUS,name='pc')
            
            # Non-negativity constraints
            m.addConstr((f >= 0),"f non-negative")
            m.addConstr((fc >= 0),"fc non-negative")
            m.addConstr((pc >= 0),"pc non-negative")
            m.addConstrs((hc[s] >= 0 for s in SS),"hc non-negative")
            m.addConstrs((tc[s] >= 0 for s in SS),"tc non-negative")
            m.addConstrs((wc[s] >= 0 for s in SS),"wc non-negative")
            
            print('define Constraint (2) ...\n')
            m.addConstrs((sum(y[a,i] * V[a] for a in AS) <= sum(x[i,l] * U[l] for l in LS) for i in IS), 
                        "Constraint (2)")
            
            print('define Constraint (3) ...\n')
            m.addConstrs((z[s,a,i] == y[a,i] - sum(q[s,a,i,j] for j in IS) for a in AS for i in IS for s in SS), 
                        "Constraint (3)")
            
            print('define Constraint (4) ...\n')
            # C03
            m.addConstrs((w[s,a,j] == D_sample[s,a,j] - sum(q[s,a,i,j] for i in IS) for a in AS for j in IS for s in SS), 
                        "Constraint (4)")
            
            print('define Constraint (5) ...\n')
            # C04
            m.addConstrs((sum(x[i,l] for l in LS) <= 1 for i in IS), "Constraint (5)")
            
            
            print('objective functions')
            # C05
            m.addConstrs((wc[s] == sum(G[a] * w[s,a,j] 
                                    for a in AS for j in IS) for s in SS), "Shortage Costs")
                
            m.addConstrs((hc[s] == sum(CH[a] * z[s,a,i] 
                                    for a in AS for i in IS) for s in SS), "Surplus Costs")
            
            m.addConstrs((tc[s] == sum(CT[a] * H[i,j] * q[s,a,i,j] 
                                    for a in AS for i in IS for j in IS) for s in SS), "Transportation Costs")
            
            print('define objective ...\n')
            
            # Objective
            m.addConstr((fc == sum(CF[l] * x[i,l] for i in IS for l in LS)), "Fixed Facility Costs")
            
            m.addConstr((pc == sum(CP[a] * y[a,i] for a in AS for i in IS)), "Procurement Costs")
            
            m.addConstr((f == fc + pc + sum(pr_sample[s] * (tc[s] + hc[s] + wc[s]) for s in SS)), "Objective Function")
            
            m.setObjective((f), GRB.MINIMIZE)
            
            print('solving ...\n')
            
            m.optimize()
            
            if m.status == GRB.OPTIMAL:
                print('solved!')
                
                Vx1 = np.zeros((IS[-1]+1,LS[-1]+1))
                Vy1 = np.zeros((AS[-1]+1,IS[-1]+1))
                for i in IS:
                    for l in LS:
                        Vx1[i,l] = x[(i,l)].x
                    for a in AS:
                        Vy1[a,i] = y[(a,i)].x

                Vf1 = m.getObjective().getValue()
                Vfc1 = sum(CF[l] * Vx1[i,l] for i in IS for l in LS)
                Vpc1 = sum(CP[a] * Vy1[a,i] for a in AS for i in IS)
                Vtc1 = sum(pr_sample[s] * tc[s].x for s in SS)
                Vhc1 = sum(pr_sample[s] * hc[s].x for s in SS)
                Vwc1 = sum(pr_sample[s] * wc[s].x for s in SS)        
                Vec1 = Vfc1+Vpc1+Vtc1+Vhc1
                
                return Vf1, Vec1, Vpc1, Vwc1, Vx1, Vy1    
            
            else:
                print('Hmm, something went wrong! Status code:', m.status)
                attempt += 1
        
        # except GurobiError as e:
        except Exception as e:
            # print('Error code ' + str(e.errno) + ": " + str(e))
            print('Encountered a Gurobi error. Please check the Gurobi log for more details.')
            attempt += 1
            
    print(f"Try to find an optimal solution for {attempt + 1} attempts.")

def renew(IS,AS,LS,NS,CF,U,V,H,CP,CH,G,CT,D,pr,new_x,new_y):
    """
    尝试解决优化模型，如果在优化过程中出现异常，将重试最多 max_attempts 次。
    """
    attempt = 0
    while attempt < max_attempts:
        try:
            # 创建新模型
            m = Model("renew")
                
            # create sets
            IS = range(IS)
            AS = range(AS)
            LS = range(LS)
            NS = range(NS)
            
            # create variables
            print('define variables ...\n')
            q = m.addVars(NS,AS,IS,IS,vtype=GRB.INTEGER, name="q")   
            z = m.addVars(NS,AS,IS,vtype=GRB.INTEGER, name="z")
            w = m.addVars(NS,AS,IS,vtype=GRB.INTEGER, name="w")
            hc = m.addVars(NS,vtype=GRB.CONTINUOUS, name="hc")
            tc = m.addVars(NS,vtype=GRB.CONTINUOUS, name="tc")
            wc = m.addVars(NS,vtype=GRB.CONTINUOUS, name="wc")
            
            # Non-negativity constraints
            m.addConstrs((q[s,a,i,j] >= 0 for s in NS for a in AS for i in IS for j in IS), "q non-negative")
            m.addConstrs((z[s,a,i] >= 0 for s in NS for a in AS for i in IS), "z non-negative")
            m.addConstrs((w[s,a,j] >= 0 for s in NS for a in AS for j in IS), "w non-negative")
            
            f = m.addVar(vtype=GRB.CONTINUOUS,name='f')
            
            # Non-negativity constraints
            m.addConstr((f >= 0),"f non-negative")
            m.addConstrs((hc[s] >= 0 for s in NS),"hc non-negative")
            m.addConstrs((tc[s] >= 0 for s in NS),"tc non-negative")
            m.addConstrs((wc[s] >= 0 for s in NS),"wc non-negative")

            print('define Constraint (3) ...\n')
            m.addConstrs((z[s,a,i] == new_y[a,i] - sum(q[s,a,i,j] for j in IS) for a in AS for i in IS for s in NS), 
                        "Constraint (3)")
            
            print('define Constraint (4) ...\n')
            # C03
            m.addConstrs((w[s,a,j] == D[s,a,j] - sum(q[s,a,i,j] for i in IS) for a in AS for j in IS for s in NS), 
                        "Constraint (4)")
            
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
            
            m.addConstr((f == sum(pr[s] * (tc[s] + hc[s] + wc[s]) for s in NS)), "Objective Function")
            
            m.setObjective((f), GRB.MINIMIZE)
            
            print('solving ...\n')
            
            m.optimize()
    
            if m.status == GRB.OPTIMAL:
                print('solved!')

                Vfc2 = sum(CF[l] * new_x[i,l] for i in IS for l in LS)
                Vpc2 = sum(CP[a] * new_y[a,i] for a in AS for i in IS)
                Vtc2 = sum(pr[s] * tc[s].x for s in NS)
                Vhc2 = sum(pr[s] * hc[s].x for s in NS)
                Vwc2 = sum(pr[s] * wc[s].x for s in NS)        
                Vf2 = Vfc2+Vpc2+Vtc2+Vhc2+Vwc2
                
                return Vf2, Vfc2, Vpc2, Vtc2, Vhc2, Vwc2
        
            else:
                print('Hmm, something went wrong! Status code:', m.status)
                attempt += 1
        
        # except GurobiError as e:
        except Exception as e:
            # print('Error code ' + str(e.errno) + ": " + str(e))
            print('Encountered a Gurobi error. Please check the Gurobi log for more details.')
            attempt += 1

    print(f"Try to find an optimal solution for {attempt} attempts.")