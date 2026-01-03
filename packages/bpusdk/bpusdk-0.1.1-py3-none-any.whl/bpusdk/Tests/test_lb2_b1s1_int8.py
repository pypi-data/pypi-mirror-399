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
from bpusdk.BrainpyLib.lb2_SNN import lb2_SNN,lb2_config
from bpusdk.BrainpyLib.BrainpyBase import BrainpyBase
from bpusdk.BrainpyLib.lb2_checkRes import lb2_checkRes
from bpusdk.BrainpyLib.lb2_deploy import lb2_deploy
from bpusdk.BrainpyLib.GenConn import gen_conn_int8_random 

warnings.filterwarnings("ignore")
random.seed(1)
bm.random.seed(42)
bm.set_dt(2.0)
def gen_net(nExc,nInh,fanOut):
    t0 = time.time()
    conn_list = gen_conn_int8_random(nExc+nInh,fanOut,groupSize=4)
    net = EINet(population_sizes=[nExc,nInh], conn=["customized",conn_list] , method = "euler")
    t1 = time.time()
    print(f"{(nExc+nInh)//1024}k network generated in {t1-t0:.2f} seconds")
    return net

if __name__ == "__main__":
    download_dir = "../data7/Lb2_int8_576k"
    upload_dir = "../upload7/ResLb2_int8_576k"
    nExc = 288*1024
    nInh = 288*1024
    fanOut = 4
    nStep = 18
    
    # Gendata
    net = gen_net(nExc,nInh,fanout)
    inpI = 100. 
           
    lb2_config = lb2_config(config={"Dtype":"int8"})                                    
    bpbase = BrainpyBase(network=net, inpI=inpI)
    bpuset = lb2_SNN(net.population_sizes, bpbase.parameterInit, bpbase.connection_matrix, bpbase.neuron_name, bpbase.compiler_input, inpI=inpI, config=lb2_config.hw_config)     
    bpuset.gen_bin_data(download_dir)
    net.dump(download_dir,nStep,inpI=inpI,save=True,jit=True)      

    # Deploy
    deploy = lb2_deploy(download_dir,upload_dir)
    sender_path = "/home/gdiist1/work/beartic/LBII_matrix/build/LBII"
    deploy.run_from_host(nStep=nStep,sender_path=sender_path,device_id=1)
    # deploy.run_from_driver(step=nStep,device_id=16,dmos=False)

    # Compare results or convert bin to npy 
    check = lb2_checkRes(download_dir, upload_dir, nStep)
    check.bin2npy()
    check.npyVSnpy(w_dump=False) 