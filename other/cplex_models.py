from docplex.mp.model import Model
import numpy as np

def getsol(IS, AS, LS, SS, CF, U, V, H, CP, CH, G, CT, D_sample, pr_sample):
    # create a new model
    m = Model("cplex_getsol")
    
    # create sets
    IS = range(IS)
    AS = range(AS)
    LS = range(LS)
    SS = range(SS)
    
    # define variables
    print('define variables ...\n')
    x = m.binary_var_matrix(IS, LS, name="x")
    y = m.integer_var_matrix(AS, IS, name="y")
    q = m.integer_var_cube(SS, AS, IS, IS, name="q")
    z = m.integer_var_matrix(SS, AS, IS, name="z")
    w = m.integer_var_matrix(SS, AS, IS, name="w")
    hc = m.continuous_var_list(len(SS), name="hc")
    tc = m.continuous_var_list(len(SS), name="tc")
    wc = m.continuous_var_list(len(SS), name="wc")
    
    # Non-negativity constraints
    m.add_constraints(y[a, i] >= 0 for a in AS for i in IS)
    m.add_constraints(q[s, a, i, j] >= 0 for s in SS for a in AS for i in IS for j in IS)
    m.add_constraints(z[s, a, i] >= 0 for s in SS for a in AS for i in IS)
    m.add_constraints(w[s, a, j] >= 0 for s in SS for a in AS for j in IS)
    
    f = m.continuous_var(name='f')
    fc = m.continuous_var(name='fc')
    pc = m.continuous_var(name='pc')
    
    # Non-negativity constraints
    m.add_constraint(f >= 0)
    m.add_constraint(fc >= 0)
    m.add_constraint(pc >= 0)
    m.add_constraints(hc[s] >= 0 for s in SS)
    m.add_constraints(tc[s] >= 0 for s in SS)
    m.add_constraints(wc[s] >= 0 for s in SS)
    
    # define constraints
    print('define constraints ...\n')
    m.add_constraints(m.sum(y[a, i] * V[a] for a in AS) <= m.sum(x[i, l] * U[l] for l in LS) for i in IS)
    m.add_constraints(z[s, a, i] == y[a, i] - m.sum(q[s, a, i, j] for j in IS) for a in AS for i in IS for s in SS)
    m.add_constraints(w[s, a, j] == D_sample[s, a, j] - m.sum(q[s, a, i, j] for i in IS) for a in AS for j in IS for s in SS)
    m.add_constraints(m.sum(x[i, l] for l in LS) <= 1 for i in IS)
    
    # define objective functions
    print('define objective functions ...\n')
    m.add_constraints(wc[s] == m.sum(G[a] * w[s, a, j] for a in AS for j in IS) for s in SS)
    m.add_constraints(hc[s] == m.sum(CH[a] * z[s, a, i] for a in AS for i in IS) for s in SS)
    m.add_constraints(tc[s] == m.sum(CT[a] * H[i, j] * q[s, a, i, j] for a in AS for i in IS for j in IS) for s in SS)
    
    # define the objective
    m.minimize(f)

    # solve the model
    print('solving ...\n')
    solution = m.solve()
    
    if solution:
        print('solved!')
        # Parse and return the solution as needed ...
    else:
        print('Hmm, something went wrong!')

def renew(IS, AS, LS, NS, CF, U, V, H, CP, CH, G, CT, D, pr, new_x, new_y):
    # create a new model
    m = Model("cplex_renew")
    
    # create sets
    IS = range(IS)
    AS = range(AS)
    LS = range(LS)
    NS = range(NS)
    
    # create variables
    print('define variables ...\n')
    q = m.integer_var_cube(NS, AS, IS, IS, name="q")
    z = m.integer_var_matrix(NS, AS, IS, name="z")
    w = m.integer_var_matrix(NS, AS, IS, name="w")
    hc = m.continuous_var_list(len(NS), name="hc")
    tc = m.continuous_var_list(len(NS), name="tc")
    wc = m.continuous_var_list(len(NS), name="wc")
    
    # Non-negativity constraints
    f = m.continuous_var(name='f')
    
    # define constraints
    print('define constraints ...\n')
    m.add_constraints(z[s, a, i] == new_y[a, i] - m.sum(q[s, a, i, j] for j in IS) for s in NS for a in AS for i in IS)
    m.add_constraints(w[s, a, j] == D[s, a, j] - m.sum(q[s, a, i, j] for i in IS) for s in NS for a in AS for j in IS)
    
    print('define objective functions ...\n')
    m.add_constraints(wc[s] == m.sum(G[a] * w[s, a, j] for a in AS for j in IS) for s in NS)
    m.add_constraints(hc[s] == m.sum(CH[a] * z[s, a, i] for a in AS for i in IS) for s in NS)
    m.add_constraints(tc[s] == m.sum(CT[a] * H[i, j] * q[s, a, i, j] for a in AS for i in IS for j in IS) for s in NS)
    
    print('define objective ...\n')
    m.minimize(m.sum(pr[s] * (tc[s] + hc[s] + wc[s]) for s in NS))
    
    print('solving ...\n')
    solution = m.solve()
    
    print('solved!\n')
    
    if solution:
        Vfc2 = sum(CF[l] * new_x[i, l] for i in IS for l in LS)
        Vpc2 = sum(CP[a] * new_y[a, i] for a in AS for i in IS)
        Vtc2 = sum(pr[s] * tc[s].solution_value for s in NS)
        Vhc2 = sum(pr[s] * hc[s].solution_value for s in NS)
        Vwc2 = sum(pr[s] * wc[s].solution_value for s in NS)
        Vf2 = Vfc2 + Vpc2 + Vtc2 + Vhc2 + Vwc2
    else:
        print('Hmm, something went wrong!')
        return None
    
    return Vf2, Vfc2, Vpc2, Vtc2, Vhc2, Vwc2
