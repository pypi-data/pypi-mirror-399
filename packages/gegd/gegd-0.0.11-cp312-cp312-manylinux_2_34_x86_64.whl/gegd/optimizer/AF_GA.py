import numpy as np
import imp
mf = imp.load_source("GA_merit_fct", "\\\\f0\\smin\\Python Scripts\\Optimization\\GA_merit_fct.py")

if __name__ == '__main__':
    from mpi4py import MPI
    
    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()

directory = "\\\\f0\\smin\\Python Scripts\\Lumerical API Codes\\2D Chiral Metasurface\\Batch\\"
result_file_name = 'GA'

import os.path

def GA(mode, batch_size, dimension, generation_limit, stop_limit=10, ns=0.5, el=0.1, ts=2, pm=0.01, starting_gen=1):
    """ mode: searching for 'min' or 'max'
        batch_size: should be divisible by 20
        dimension: number of parameters to be optimized
        iteration_limit: max number of total iterations
        stop_limit: number of identical chromosomes required for termination
        ns: percentage of chromosomes that survives
        el: percentage of survivors that are preserved w/out mutation
        ts: number of genes in tournament selection
        pm: mutation probability of each gene """
    
    generation_count = starting_gen
    
    if rank == 0: #Only on head process
        #Chromosome Initialization
        if os.path.exists(directory + result_file_name + '_chromosome.npy'):
            chromosome = np.load(directory + result_file_name + '_chromosome.npy')
        else:
            chromosome = np.random.randint(2, size=(dimension, batch_size))
        if os.path.exists(directory + result_file_name + '_best_cost.npy'):
            best_cost = np.load(directory + result_file_name + '_best_cost.npy')
        cost = np.zeros(batch_size)
        with open(directory + 'chromosome_sent.txt', 'w') as f:
            f.write("--> chromosomes sent from the root\n")
        with open(directory + 'results_received.txt', 'w') as f:
            f.write("--> results received on the root\n")
    
    while True:
        if rank == 0:
            with open(directory + 'chromosome_sent.txt', 'a') as f:
                f.write("Generation: %d\n" % generation_count)
                for dim in range(dimension):
                    for s in range(1):
                        f.write("%f\t" % chromosome[dim,s])
                    f.write("\n")
                f.write("\n")
                
                quo, rem = divmod(batch_size, size)
                data_size = [quo + 1 if p < rem else quo for p in range(size)]
                data_size = np.array(data_size)
                data_disp = [sum(data_size[:p]) for p in range(size)]
                data_disp = np.array(data_disp)
        else:
            chromosome = None
            chromosome_temp = None
            data_size = np.zeros(size, dtype=np.int)
            data_disp = None
            dimension = 0
            
        comm.Bcast(data_size, root=0)
        dimension = comm.bcast(dimension, root=0)
        
        chromosome_recv = np.zeros((dimension, data_size[rank]))
        for dim in range(dimension):
            if rank == 0:
                chromosome_temp = chromosome[dim,:]
            comm.Scatterv([chromosome_temp, data_size, data_disp, MPI.DOUBLE], chromosome_recv[dim,:], root=0)
            
        cost_temp = np.zeros(data_size[rank])
        for i in range(data_size[rank]):
            cost_temp[i] = mf.fom(chromosome_recv[:,i]).calculate_fom()
        
        cost_all_temp = np.zeros(batch_size)
        comm.Gatherv(cost_temp, [cost_all_temp, data_size, data_disp, MPI.DOUBLE], root=0)
        
        if rank == 0:
            cost = cost_all_temp.copy()
            with open(directory + 'results_received.txt', 'a') as f:
                f.write("Generation: %d\n" % generation_count)
                for i in range(size):
                    f.write("%f\t" % cost[i])
                f.write("\n")
            
            #Natural Selection (sorting)
            sorted_index = np.argsort(cost)
            if mode == 'max':
                sorted_index = np.flipud(sorted_index)
            cost = cost[sorted_index]
            chromosome = chromosome[:,sorted_index]
            if generation_count == 1:
                best_cost = cost[0]
                best_chromosome = chromosome[:,-1]
            else:
                best_cost = np.append(best_cost, cost[0])
            best_chromosome = chromosome[:,0]
            
            #Write Results into Text File (optional)
            if generation_count == 1:
                with open(directory + 'GA_best_' + result_file_name + '.txt', 'w') as f:
                    f.write('Generation %d:\t' % generation_count)
                    f.write(np.format_float_scientific(best_cost))
                    f.write('\t\t')
                    for dim in range(dimension):
                        f.write('%d,' % int(best_chromosome[dim]))
                    f.write('\n')
            else:
                with open(directory + 'GA_best_' + result_file_name + '.txt', 'a') as f:
                    f.write('Generation %d:\t' % generation_count)
                    f.write(np.format_float_scientific(best_cost[-1]))
                    f.write('\t\t')
                    for dim in range(dimension):
                        f.write('%d,' % int(best_chromosome[dim]))
                    f.write('\n')
            
        generation_count += 1
        
        #Termination Condition
        if generation_count > generation_limit:
            break
        stop_count = 1
        if rank == 0:
            for i in range(1, batch_size):
                if cost[i] == cost[0]:
                    stop_count += 1
        stop_count = comm.bcast(stop_count, root=0)
        if stop_count >= stop_limit:
            break
        
        if rank == 0:
            for i in range(int(batch_size*ns*el), batch_size):
                if i >= int(batch_size*ns):
                    #Tournament Selection
                    gene_ts_final = np.zeros(2).astype(int)
                    while True:
                        if gene_ts_final[0] != gene_ts_final[1]:
                            break
                        gene_ts_final = np.zeros(2).astype(int)
                        for j in range(2):
                            gene_ts = np.random.randint(0, int(batch_size*ns), size=(ts))
                            cost_ts = cost[gene_ts]
                            sorted_index = np.argsort(cost_ts)
                            if mode == 'max':
                                sorted_index = np.flipud(sorted_index)
                            gene_ts_final[j] = gene_ts[sorted_index[0]]
                    
                    #Reproduction
                    cut1 = np.random.randint(0, dimension)
                    cut2 = np.random.randint(cut1+1, dimension+1)
                    chromosome[:cut1,i] = chromosome[:cut1,gene_ts_final[0]]
                    chromosome[cut1:cut2,i] = chromosome[cut1:cut2,gene_ts_final[1]]
                    chromosome[cut2:,i] = chromosome[cut2:,gene_ts_final[0]]
                
                #Mutation
                for j in range(dimension):
                    if np.random.random() < pm:
                        if chromosome[j,i] == 0:
                            chromosome[j,i] = 1
                        else:
                            chromosome[j,i] = 0
    
    return best_chromosome, best_cost

if __name__ == '__main__':
    best_chromosome, best_cost = GA(mode='max', batch_size=20, dimension=9, generation_limit=50, starting_gen=1)