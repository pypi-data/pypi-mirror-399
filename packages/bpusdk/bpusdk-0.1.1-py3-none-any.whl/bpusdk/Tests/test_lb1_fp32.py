import time
import warnings
import brainpy.math as bm
import numpy as np
import random
import os 
import sys

current_path = os.getcwd()
sys.path.insert(0, current_path)
from bpusdk.Models.EImodel import EINet
from bpusdk.BrainpyLib.lb1_SNN import lb1_SNN,lb1_config
from bpusdk.BrainpyLib.BrainpyBase import BrainpyBase
from bpusdk.BrainpyLib.lb1_deploy import lb1_deploy
from bpusdk.BrainpyLib.lb1_checkRes import lb1_checkRes
from bpusdk.BrainpyLib.GenConn import gen_conn_random 

warnings.filterwarnings("ignore")
random.seed(1)
bm.random.seed(42)
bm.set_dt(1.0)

def gen_net(nExc,nInh,fanout):
    t0 = time.time()
    conn_list = gen_conn_random(nExc+nInh,fanout)
    net = EINet(population_sizes=[nExc,nInh], conn=["customized",conn_list] , method = "euler")
    t1 = time.time()
    print(f"{nExc+nInh//1024}k network generated in {t1-t0:.2f} seconds")
    return net

if __name__ == "__main__":
    download_dir = "../data7/lb1_96k"
    upload_dir = "../upload7/Reslb1_96k"
    nExc = 48*1024
    nInh = 48*1024
    fanout = 2
    nStep = 5

    # Gendata
    net = gen_net(nExc,nInh,fanout)
    inpI = 100.       
                       
    config = lb1_config()            
    bpbase = BrainpyBase(network=net, inpI=inpI)
    bpuset = lb1_SNN(net.population_sizes, bpbase.parameterInit, bpbase.connection_matrix, bpbase.neuron_name, bpbase.compiler_input, inpI=inpI, config=config.hw_config)     
    bpuset.gen_bin_data(download_dir)
    net.dump(download_dir,nStep,inpI=inpI,save=True,jit=True)  
    
    # # Deploy
    # deploy = lb1_deploy(download_dir,upload_dir)
    # sender_path = "/root/work/sender/gdiist_host/zcu102_sender"
    # deploy.run_from_host(nStep=nStep,device_id=4,run=True,sender_path=sender_path)

    # # # Compare results or convert bin to npy
    # check = lb1_checkRes(download_dir, upload_dir, nStep)
    # hw_s,hw_v = check.bin2npy()
    # check.npyVSnpy() 