import time
import warnings
import brainpy.math as bm
import numpy as np
import random
import os 
import sys

current_path = os.getcwd()
sys.path.insert(0, current_path)
from bpusdk.Models.EImodel_HHtemp import EINet
from bpusdk.BrainpyLib.lb2_SNN import lb2_SNN,lb2_config
from bpusdk.BrainpyLib.BrainpyBase import BrainpyBase
from bpusdk.BrainpyLib.lb2_checkRes import lb2_checkRes
from bpusdk.BrainpyLib.lb2_deploy import lb2_deploy
from bpusdk.BrainpyLib.GenConn import gen_conn_random 
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")
random.seed(1)
bm.random.seed(42)
dt = 0.005
bm.set_dt(dt)

def gen_net(nExc,nInh,temp):
    t0 = time.time()  
    data = [np.array([])]
    conn = ["customized",data] 
    net = EINet(population_sizes=[nExc,nInh], conn=conn, method = "euler",temp=temp)
    t1 = time.time()
    print(f"{nExc+nInh//1024}k network generated in {t1-t0:.2f} seconds")
    return net

if __name__ == "__main__":
    download_dir = "../data7/Lb2_mode3_HHtemp_55_5000_new"
    upload_dir = "../upload7/ResLb2_mode3_HHtemp_55_5000_new"
    nExc = 1
    nInh = 0
    nStep = 5000
    temp = 55

    # # Gendata
    net = gen_net(nExc,nInh,temp)
    inpI = 0.       
    lb2_config = lb2_config()    
    bpbase = BrainpyBase(network=net, inpI=inpI)                             
    bpuset = lb2_SNN(net.population_sizes, bpbase.parameterInit, bpbase.connection_matrix, bpbase.neuron_name, bpbase.compiler_input, inpI=inpI, config=lb2_config.hw_config,mode=3)     
    bpuset.gen_bin_data(download_dir)
    net.dump(download_dir,nStep,inpI=inpI)     

    # Deploy
    deploy = lb2_deploy(download_dir,upload_dir)
    sender_path = "/home/gdiist1/work/beartic/LBII_matrix/build/LBII"
    deploy.run_from_host(nStep=nStep,sender_path=sender_path,device_id=0,run=False)
    # deploy.run_from_driver(nStep=nStep,device_id=0,dmos=False)

    # # # Compare results or convert bin to npy
    check = lb2_checkRes(download_dir, upload_dir, nStep,single_neuron=True)
    [hw_v] = check.bin2npy(spike_dump=False,prefix="1")
    errorflag = check.npyVSnpy(s_dump=False,w_dump = False,print_log=True)
    print(f"Error flag: {errorflag}")
    
    plt.subplot(3,1,1)
    plt.plot(hw_v[:,0])
    plt.title('hw_v')
    
    plt.subplot(3,1,2)
    sw_output_path = download_dir + "/soft_data"
    sw_v     = np.load(sw_output_path+"/N_V.npy").astype(np.float32)
    plt.plot(sw_v[:,0])
    plt.title('sw_v')
  
    plt.subplot(3,1,3)
    sw_output_path = download_dir + "/soft_data"
    diff     = np.abs(hw_v[:,0]-sw_v[:,0])
    plt.plot(diff[:])
    plt.title('diff')
    
    plt.tight_layout()    
    plt.savefig("./55_5000.png", dpi=300)
