import dimod
#from dwave.system import EmbeddingComposite, DWaveSampler
from dimod import BinaryQuadraticModel, ExactSolver
from sklearn import preprocessing
#import xlrd

#book = xlrd.open_workbook('containers.xlsx')
#sheet = book.sheet_by_index(0)

t = [0.5, 0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
m = [769.0, 836.0, 2134.0, 3455.0, 1866.0, 1699.0, 3500.0, 3332.0, 2578.0, 2315.0, 1888.0, 1786.0, 3277.0, 2987.0, 2534.0, 2111.0, 2607.0, 1566.0, 1765.0, 1946.0, 1732.0, 1641.0, 1800.0, 986.0, 873.0, 1764.0, 1239.0, 1487.0, 659.0, 765.0]

non_norm_m = m
#for i in range(15):
#    t.append(sheet.cell(i+1, 1).value)
#    m.append(sheet.cell(i+1, 2).value)
#for i in range(15):
#    t.append(sheet.cell(i + 1, 4).value)
#    m.append(sheet.cell(i + 1, 5).value)

h_a_dict = {}
J_a_b_dict = {}

L = 1
N = 2
n = 2

W_p = 40*10**3
W_e = 120*10**3
non_norm_W_p = W_p
non_norm_W_e = W_e
m.append(W_p)
m.append(W_e)
m = preprocessing.normalize([m])[0]
W_p, W_e, m = m[-2], m[-1], m[:-2]

x_cg_e = -0.05*L
x_cg_min = -0.1*L
x_cg_max = 0.2*L
x_cg_t = 0.1*L

S_0_max = 22*10**3

theta_mass = 10
theta_space = 10
theta_one_to_one = 5
theta_target_x = 0.5
for i in range(n):
    for k in range(N):
        j = -N/2+0.5 + k
        h_a_dict['Z{}_{}'.format(i, j)] = theta_mass*(-2*W_p*m[i] + m[i]**2)+theta_space*(- 2*N*t[i] + t[i]**2) + W_e*(x_cg_e - x_cg_max)*m[i]*(L/N*j-x_cg_min) + \
            W_e*(x_cg_e - x_cg_min)*m[i]*(L/N*j-x_cg_max) + m[i]**2*(L/N*j - x_cg_min)*(L/N*j - x_cg_max) + \
            theta_target_x*(2*W_e*(x_cg_e - x_cg_t)*m[i]*(L/N*j-x_cg_t) + m[i]**2*(L/N*j-x_cg_t)**2) + theta_one_to_one*(t[i] + 1)
        for i_1 in range(n):
            for k_1 in range(N):
                j_1 = -N/2+0.5 + k_1
                J_a_b_dict['Z{}_{}'.format(i, j),
                           'Z{}_{}'.format(i_1, j_1)] = theta_mass*(2*m[i]*m[i_1]) + theta_space*(2*t[i]*t[i_1]) + 2*m[i]*m[i_1]*(L/N*j-x_cg_min)*(L/N*j_1-x_cg_max) + \
                    theta_target_x*(2*m[i]*m[i_1]*(L/N*j-x_cg_t)*(L/N*j_1-x_cg_t))

gamma = theta_mass*(W_p**2)+theta_space*(N**2) + W_e**2*(x_cg_e - x_cg_min)*(x_cg_e - x_cg_max) + theta_target_x*(W_e**2*(x_cg_e - x_cg_t)**2) +theta_one_to_one*(- N - n)

BQM = dimod.BinaryQuadraticModel(h_a_dict, J_a_b_dict, gamma, 'BINARY')

sampler = ExactSolver()
sampled = sampler.sample(BQM)
#print(sampled)

#ising_model = BQM.to_ising()
#sampler = EmbeddingComposite(DWaveSampler())
#sampled = sampler.sample_ising(h = ising_model[0], J = ising_model[1], num_reads = 100)
print(sampled)

loaded_mass = []
loaded_coord = []
print()
for a in range(4):
    print("{} energy".format(a))
    for k in range(N):
        j = -N / 2 + 0.5 + k
        flag = False
        for i in range(n):
            if sampled.slice(a, a+1).first.sample['Z{}_{}'.format(i, j)] == 1:
                print(j, non_norm_m[i], t[i])
                loaded_mass.append(non_norm_m[i])
                loaded_coord.append(L/N*j)
                flag = True
        if not flag:
            print(j)

    x = (non_norm_W_e*x_cg_e + sum([a*b for a,b in zip(loaded_mass, loaded_coord)]))/(non_norm_W_e + sum(loaded_mass))
    print('Коорд. x ц.т.', round(x, 4))
    print('Загрузка', int(sum(loaded_mass)), 'из', non_norm_W_p)
    print('Условие кр. сд. вып.')
    loaded_mass = []
    loaded_coord = []
    print()
