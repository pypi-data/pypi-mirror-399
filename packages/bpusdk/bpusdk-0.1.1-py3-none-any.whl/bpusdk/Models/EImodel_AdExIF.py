import warnings
from pathlib import Path
import brainpy as bp
import numpy as np
from brainpy import math as bm
import pickle
from bpusdk.BrainpyLib.BrainpyBase import BrainpyBase

warnings.filterwarnings('ignore')

class Exponential(bp.Projection):
    def __init__(self, nNeuron, pre, post, delay, conn, g_max, tau, E, method, allow_multi_conn):
        super().__init__()
        conn = self.createConn(nNeuron, conn, pre, post,allow_multi_conn)
        self.pron = bp.dyn.FullProjAlignPost(
            pre=pre,
            delay=delay,
            comm=bp.dnn.EventCSRLinear(conn, g_max),
            syn=bp.dyn.Expon(size=post.num, tau=tau,method=method),  
            out=bp.dyn.CUBA(),          
            post=post
        )

    def createConn_by_prepost(self, nNeuron, prob, pre, post, allow_multi_conn):
        pre_list_ori,post_list_ori = prob  
        ii_pre = np.where(pre_list_ori<nNeuron[0]) if pre.name[-1] == '0' else np.where(pre_list_ori>=nNeuron[0])
        ii_post = np.where(post_list_ori<nNeuron[0]) if post.name[-1] == '0' else np.where(post_list_ori>=nNeuron[0])
        ii = set(ii_pre[0]) & set(ii_post[0])
        ii = np.array(list(ii))

        if len(ii) == 0: 
            conn = bp.conn.FixedProb(0, pre=pre.num, post=post.num, allow_multi_conn=True) 
        
        else:
            pre_list = pre_list_ori[ii]
            offset_pre = 0 if pre.name[-1] == '0' else nNeuron[0]
            pre_list -= offset_pre

            post_list = post_list_ori[ii]
            offset_post = 0 if post.name[-1] == '0' else nNeuron[0]
            post_list -= offset_post

            conn = bp.conn.IJConn(i=pre_list, j=post_list)
            conn = conn(pre_size=pre.num, post_size=post.num)
        return conn

    def createConn(self, nNeuron, conn, pre, post, allow_multi_conn):
        match conn[0]:
            case 'customized':
                conn = self.createConn_by_prepost(nNeuron, conn[1], pre, post, allow_multi_conn)
            case 'FixedPreNum': 
                conn = bp.conn.FixedPreNum(conn[1], pre=pre.num, post=post.num, allow_multi_conn=allow_multi_conn)
            case 'FixedPostNum':  
                conn = bp.conn.FixedPostNum(conn[1], pre=pre.num, post=post.num, allow_multi_conn=allow_multi_conn)
            case 'FixedTotalNum': 
                conn = bp.conn.FixedTotalNum(conn[1], pre=pre.num, post=post.num, allow_multi_conn=allow_multi_conn)
            case 'FixedProb':   
                conn = bp.conn.FixedProb(conn[1], pre=pre.num, post=post.num, allow_multi_conn=allow_multi_conn)
            case 'FixedPostNum':   
                conn = bp.conn.FixedPostNum(conn[1], pre=pre.num, post=post.num, allow_multi_conn=allow_multi_conn)
            case _:
                print(f"conn is of unsupported type")     
        return conn

class EINet(bp.DynamicalSystem):
    def __init__(self, population_sizes, conn, method, allow_multi_conn=False):
        super().__init__()
        self.initState = bm.random.DEFAULT.value
        self.population_sizes = population_sizes 
        #tauRef = bm.get_dt()*4.+0.0001 # Make sure tauRef always == 5 timesteps 
        tauRef = 0+0.0001 
        self.E = bp.dyn.AdExIF(population_sizes[0], V_rest= -70., V_th=0., V_T=-50., delta_T=2., R=0.5,  
                                a=-0.5, b=7, tau=5., tau_w=100., V_reset=-47.,
                                V_initializer=bp.init.Uniform(-100.,-17.5), 
                                # w_initializer=bp.init.Constant(2.2),
                                method=method)

        self.I = bp.dyn.AdExIF(population_sizes[1], V_rest= -70., V_th=0., V_T=-50., delta_T=2., R=0.5,  
                                a=-0.5, b=7, tau=5., tau_w=100., V_reset=-47.,
                                V_initializer=bp.init.Uniform(-100.,-17.5), 
                                # w_initializer=bp.init.Constant(2.2),
                                method=method)        
        
        self.E2E = Exponential(self.population_sizes, self.E, self.E, delay=0.,
                               conn=conn, g_max=1, tau=5., E=0.,method=method,allow_multi_conn=allow_multi_conn)
        self.E2I = Exponential(self.population_sizes, self.E, self.I, delay=0.,
                               conn=conn, g_max=1, tau=5., E=0.,method=method,allow_multi_conn=allow_multi_conn)
        self.I2E = Exponential(self.population_sizes, self.I, self.E, delay=0.,
                               conn=conn, g_max=6, tau=10., E=-80.,method=method,allow_multi_conn=allow_multi_conn)
        self.I2I = Exponential(self.population_sizes, self.I, self.I, delay=0.,
                               conn=conn, g_max=6, tau=10., E=-80.,method=method,allow_multi_conn=allow_multi_conn)
    
    def force_init(self,target,id_list):
        mask = id_list < self.population_sizes[0]
        id_list_E = id_list[mask]
        id_list_I = id_list[~mask]-self.population_sizes[0]
                
        padding = np.zeros(self.population_sizes[0])
        padding[id_list_E] = target - self.E.V.value[id_list_E]
        self.E.V.value += padding
            
        padding = np.zeros(self.population_sizes[0])
        padding[id_list_I] = target - self.I.V.value[id_list_I]
        self.I.V.value += padding

    def update(self, inpS, inpI):
        inpS = inpS.astype(bool)
        self.E2E.pron.refs['pre'].spike.value += inpS[:self.population_sizes[0]]
        self.E2I.pron.refs['pre'].spike.value += inpS[:self.population_sizes[0]]
        self.I2E.pron.refs['pre'].spike.value += inpS[self.population_sizes[0]:]
        self.I2I.pron.refs['pre'].spike.value += inpS[self.population_sizes[0]:]

        self.E2E()
        self.E2I()
        self.I2E()
        self.I2I()
        self.E(inpI)
        self.I(inpI)
        return self.E.spike, self.I.spike

    def dump(self,download_path,nStep,inpS=None,inpI=0,jit=True,save=True,txt=False): 
        if inpS is None:
            inpS = np.zeros((int(nStep), np.sum(self.population_sizes))).astype(bool) 
        else: 
            tmp_impS = inpS
            inpS = np.zeros((int(nStep), np.sum(self.population_sizes)))
            inpS[:tmp_impS.shape[0],:tmp_impS.shape[1]] = tmp_impS
            inpS = inpS.astype(bool)

        V_init = np.concatenate((self.E.V.value, self.I.V.value), axis=0)
        V_init = np.expand_dims(V_init, axis=0)
        S_init = np.zeros((1, np.sum(self.population_sizes)))
        w_init = np.concatenate((self.E.w.value, self.I.w.value), axis=0)
        w_init = np.expand_dims(w_init, axis=0)
        wacc_init = np.zeros((1, np.sum(self.population_sizes)))
        runner = bp.DSRunner(self, monitors=['E.spike', 'I.spike', 'E.w','I.w','E.V', 'I.V','E2E.pron.syn.g','E2I.pron.syn.g','I2E.pron.syn.g','I2I.pron.syn.g'], jit=jit)#
        _ = runner.predict(inputs=[inpS, bm.ones(nStep) * inpI])

        E_sps = runner.mon['E.spike']
        I_sps = runner.mon['I.spike']
        E_V = runner.mon['E.V']
        I_V = runner.mon['I.V']
        E_w = runner.mon['E.w']
        I_w = runner.mon['I.w']
        E2E = runner.mon['E2E.pron.syn.g']
        E2I = runner.mon['E2I.pron.syn.g']
        I2E = runner.mon['I2E.pron.syn.g']
        I2I = runner.mon['I2I.pron.syn.g']
        
        S = np.concatenate((E_sps, I_sps), axis=1)
        S = np.concatenate((S_init, S), axis=0)
        V = np.concatenate((E_V, I_V), axis=1)
        V = np.concatenate((V_init, V), axis=0)
        w = np.concatenate((E_w, I_w), axis=1)
        w = np.concatenate((w_init, w), axis=0)
        wacc1 = np.concatenate((E2E, E2I), axis=1)
        wacc1 = np.concatenate((wacc_init, wacc1), axis=0)
        wacc1 *= (1-bm.get_dt()/self.E2E.pron.syn.tau)
        wacc2 = np.concatenate((I2E, I2I), axis=1)
        wacc2 = np.concatenate((wacc_init, wacc2), axis=0)
        wacc2 *= (1-bm.get_dt()/self.I2E.pron.syn.tau)

        if save == True:
          download_path = f"{download_path}/soft_data"
          download_dir = Path(download_path)
          download_dir.mkdir(exist_ok=True,parents=True)
          np.save(download_dir / "N_V.npy", V)
          np.save(download_dir / "N_spike.npy", S)
          np.save(download_dir / "N_wacc1.npy", wacc1)
          np.save(download_dir / "N_wacc2.npy", wacc2)
          np.save(download_dir / "N_w.npy", w)
          
          test = BrainpyBase(self, inpI)
          conn_matrix = test.get_connection_matrix()
          with open(f'{download_dir}/connection.pickle', 'wb') as handle:
              pickle.dump(conn_matrix, handle, protocol=pickle.HIGHEST_PROTOCOL)

        else:
          S = np.sum(S,axis=1)
          print(S)
        
        if txt == True:
          download_path = f"{download_path}/soft_data_txt"
          download_dir = Path(download_path)
          download_dir.mkdir(exist_ok=True,parents=True)        
          for iStep in range(nStep+1):
            np.savetxt(f"{download_path}/V_step_{iStep:03}.txt", V[iStep,:],fmt="%.6f")
            np.savetxt(f"{download_path}/S_step_{iStep:03}.txt", S[iStep,:],fmt="%.0f")

              
          # import matplotlib.pyplot as plt
          # plt.figure(figsize=(12, 4.5))
          # indices = np.arange(nStep)
          # ts = indices * bm.get_dt()
          # plt.subplot(121)
          # bp.visualize.raster_plot(ts, E_sps, show=False)
          # plt.subplot(122)
          # bp.visualize.raster_plot(ts, I_sps, show=True)
          # plt.savefig("tmp")
