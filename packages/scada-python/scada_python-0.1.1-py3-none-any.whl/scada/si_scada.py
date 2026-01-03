import numpy as np
import torch
import yaml
from tqdm import tqdm
import scada.utils.construct_interval as construct_interval
from .utils.kmeans import kmeans
import gendata
from .models.wdgrl import WDGRL
import scada.utils.util as util

device = "cpu"

def vec(A):
    vec = A.reshape(-1)
    return vec.reshape(-1,1)

def test_statistic(X_vec, Xt, ns, nt, d, n_clusters, Sigma, labels_all_obs,return_sign=False, pair=None):
    if pair is not None:
        c1, c2 = pair
    else:
        c1, c2 = np.random.choice(n_clusters, 2, replace=False)
    idx_cluster_c1 = np.argwhere(labels_all_obs[-1][ns:] == c1).flatten()
    idx_cluster_c2 = np.argwhere(labels_all_obs[-1][ns:] == c2).flatten()
    if idx_cluster_c1.size == 0 or idx_cluster_c2.size == 0:
        raise ValueError("The clusters do not contains target's samples. The model may be performed poorly or source and target distributions are too different.")

    I_d = np.identity(d)
    
    eta_c1_idx = np.zeros((nt, 1))
    eta_c1_idx[idx_cluster_c1] = 1 / len(idx_cluster_c1)
    eta_c1 = np.kron(I_d, eta_c1_idx)
    
    
    eta_c2_idx = np.zeros((nt, 1))
    eta_c2_idx[idx_cluster_c2] = 1 / len(idx_cluster_c2)
    eta_c2 = np.kron(I_d, eta_c2_idx)
   
    eta_tmp = (eta_c1 - eta_c2)
    sign_tmp = np.dot(eta_tmp.T, vec(Xt))
    sign = np.sign(sign_tmp).astype(int)
    if return_sign:
        return sign
    eta_sign = np.dot(eta_tmp, sign)

    eta = np.vstack((np.zeros((ns*d, 1)), eta_sign))
    etaTXvec = np.dot(eta.T, X_vec)

    etaT_Sigma_eta = np.dot(np.dot(eta.T, Sigma), eta)
    b = np.dot(np.dot(Sigma, eta), np.linalg.inv(etaT_Sigma_eta))
    a = np.dot(np.identity(X_vec.shape[0]) - np.dot(b, eta.T), X_vec)
    z = etaTXvec.item()
    
    return {
        "a": a,
        "b": b,
        "eta_tmp": eta_tmp,
        "zobs": z,
        "etaT_Sigma_eta": etaT_Sigma_eta.item(),
        "c1": c1,
        "c2": c2,
        "cluster_c1_obs": idx_cluster_c1,
        "cluster_c2_obs": idx_cluster_c2,
        "sign": sign
    }

def overconditioning(model,ns, X, eta, a, b, n_clusters, initial_centroids_obs, labels_all_obs, members_all_obs,z=0,X_=None):
    interval_da, a_, b_ = construct_interval.ReLUcondition(model.encoder, a, b, X)
    interval_kmean = construct_interval.KMeancondition2(X.shape[0], n_clusters, a_, b_, initial_centroids_obs, labels_all_obs, members_all_obs,z)
    interval_test_statistic = construct_interval.statistic_condition(eta, vec(a[ns:]), vec(b[ns:]), vec(X[ns:]))
    # print("interval_da", interval_da)
    # print("interval_kmean", interval_kmean)
    # print("interval_test_statistic", interval_test_statistic)
    final_interval = util.interval_intersection(interval_test_statistic,
                      util.interval_intersection(interval_da, interval_kmean))
    return final_interval
def parametric(model,ns, X, a, b, eta, n_clusters, c1, c2, c1_obs, c2_obs, signobs, zmin = -20, zmax = 20, log=None, seed=None):
    global device
    n, d = X.shape
    z =  zmin
    zmax = zmax
    countitv=0
    Z = []
    stepsize= 0.00001

    total_steps = int((zmax - zmin) / stepsize)
    with tqdm(total=total_steps, desc="Progress: ") as pbar:
        while z < zmax:
            z += stepsize
            # print("z =",z)
            Xdeltaz = a + b*z
            Xdeltaz_torch = torch.from_numpy(Xdeltaz).double().to(device)
            with torch.no_grad():
                Xdeltaz_transformed = model.extract_feature(Xdeltaz_torch).cpu().numpy()
            initial_centroids_z, labels_all_z, members_all_obs = kmeans(Xdeltaz_transformed, n_clusters)

            sign_z = np.sign(eta.T.dot(vec(Xdeltaz[ns:])))
            oc = overconditioning(model,ns, Xdeltaz, eta, a, b, n_clusters, initial_centroids_z, labels_all_z, members_all_obs, z=z,X_=Xdeltaz_transformed)
            idx_cluster_c1 = np.argwhere(labels_all_z[-1][ns:] == c1).flatten()
            idx_cluster_c2 = np.argwhere(labels_all_z[-1][ns:] == c2).flatten()

            if np.array_equal(c1_obs, idx_cluster_c1) and np.array_equal(c2_obs, idx_cluster_c2) and np.array_equal(signobs, sign_z):
                Z = util.interval_union(Z, oc)
                countitv+=1

            z = oc[-1][1]
            pbar.update(int((z - zmin) / stepsize) - pbar.n)
    return Z

def kmeans_withDA():
    pass
def run_scada(Xs, 
              Xt, 
              Sigma, 
              n_clusters, 
              labels_all_obs, 
              model_path,
              hypothesis= None,
              ):
    
    ns = Xs.shape[0]
    nt = Xt.shape[0]
    d = Xs.shape[1]
    n = ns + nt
    K = n_clusters
    with open(model_path+"/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    model_cfg = config["model"]
    final_model = WDGRL(
        input_dim=d,
        encoder_hidden_dims=model_cfg["encoder_hidden_dims"],
        critic_hidden_dims=model_cfg["critic_hidden_dims"],
        alpha1=model_cfg["alpha1"],
        alpha2=model_cfg["alpha2"],
        device=device,
    )

    final_model.load_model(model_path)
    
    Xs_vec = vec(Xs)
    Xt_vec = vec(Xt)
    X_vec = np.vstack((Xs_vec, Xt_vec))
    X_origin = np.vstack((Xs, Xt))

    a, b, eta_tmp, etaTX, etaT_Sigma_eta, c1, c2, c1_obs, c2_obs, sign = test_statistic(X_vec, Xt, ns, nt, d, K, Sigma, labels_all_obs, pair=hypothesis).values()
    

    a_2d = a.reshape(n, d)
    b_2d = b.reshape(n, d)

    std = np.sqrt(etaT_Sigma_eta)

    # final_interval = overconditioning(final_model, X_origin,eta_tmp, a_2d, b_2d,np_wdgrl, K, initial_centroids_obs, labels_all_obs, members_all_obs,z=etaTX, X_=X_transformed)
    final_interval = parametric(final_model, ns,
                                X_origin, 
                                a_2d, 
                                b_2d,
                                eta_tmp,
                                K, c1, c2, c1_obs, c2_obs, 
                                signobs = sign, 
                                zmin=-20*std, zmax=20*std,)

    selective_p_value = util.compute_p_value(final_interval, etaTX, etaT_Sigma_eta)
    return selective_p_value