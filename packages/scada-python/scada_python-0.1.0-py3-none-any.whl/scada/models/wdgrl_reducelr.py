import torch
import torch.nn as nn
from typing import List, Dict, Any
import numpy as np
from tqdm.auto import trange
from torch.utils.data import TensorDataset
import os
import random
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score
from torch.optim.lr_scheduler import ReduceLROnPlateau

def set_seed(seed: int):
    """Sets the seed for reproducibility across multiple libraries."""
    os.environ['PYTHONHASHSEED'] = str(seed)  # Python hash seed
    random.seed(seed)                        # Python's random module
    np.random.seed(seed)                     # NumPy
    torch.manual_seed(seed)                  # PyTorch CPU
    torch.cuda.manual_seed(seed)             # PyTorch CUDA (for a single GPU)
    torch.cuda.manual_seed_all(seed)         # PyTorch CUDA (for all GPUs)
    
    # Configure PyTorch for deterministic behavior
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


class Encoder(nn.Module):
    def __init__(self, input_dim: int, hidden_dims: List[int]):
        """Feature extractor network."""
        super().__init__()
        layers = []
        prev_dim = input_dim
        
        for i, hidden_dim in enumerate(hidden_dims):
            layers.append(nn.Linear(prev_dim, hidden_dim))
            if i < len(hidden_dims) - 1:  # only add ReLU for intermediate layers
                layers.append(nn.ReLU())
            prev_dim = hidden_dim

        self.net = nn.Sequential(*layers)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)

    def get_all_weights(self):
        """
        Return a list of (weight, bias) for all Linear layers.
        """
        return [layer.weight for layer in self.net if isinstance(layer, nn.Linear)]

class Critic(nn.Module):
    def __init__(self, input_dim: int, hidden_dims: List[int]):
        """Domain critic network."""
        super().__init__()
        layers = []
        prev_dim = input_dim

        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(),
            ])
            prev_dim = hidden_dim

        layers.extend([
            nn.Linear(prev_dim, 1),
            # nn.Sigmoid(),
        ])
        self.net = nn.Sequential(*layers)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class WDGRL():
    def __init__(
            self,
            input_dim: int,
            encoder_hidden_dims: List[int]=[10], 
            critic_hidden_dims: List[int]=[10, 10],
            alpha1: float = 1e-4, # critic
            alpha2: float = 1e-4, # encoder
            device: str = 'cuda' if torch.cuda.is_available() else 'cpu',
            reallabel= None,
            seed = None,
            n_clusters = 3,
            reduce_lr_on: bool = False, # <--- NEW PARAMETER
            ):

        
        self.device = device
        
        if seed is not None:
            set_seed(seed)

        self.encoder = Encoder(input_dim, encoder_hidden_dims).to(self.device).double()
        self.critic = Critic(encoder_hidden_dims[-1], critic_hidden_dims).to(self.device).double()
        
        # Optimizers
        self.encoder_optimizer = torch.optim.Adam(self.encoder.parameters(), lr=alpha2)
        self.critic_optimizer = torch.optim.Adam(self.critic.parameters(), lr=alpha1)

        # Learning Rate Schedulers (NEW)
        self.reduce_lr_on = reduce_lr_on
        if self.reduce_lr_on:
            self.encoder_scheduler = ReduceLROnPlateau(self.encoder_optimizer, mode='min', factor=0.5, patience=100, )
            self.critic_scheduler = ReduceLROnPlateau(self.critic_optimizer, mode='min', factor=0.5, patience=100, )

        self.reallabel = reallabel
        self.n_clusters = n_clusters

    def check_metric(
            self,
            Xs,
            Xt,
            epoch,
            n_cluster:int =2,
            ) -> Dict[str, Any]:
        if self.reallabel is None:
            return -1
        ns = len(Xs)


        xs_hat = self.extract_feature(Xs.tensors[0].to(self.device))
        xt_hat = self.extract_feature(Xt.tensors[0].to(self.device))
        xs_hat = xs_hat.cpu().numpy()
        xt_hat = xt_hat.cpu().numpy()

        x_comb = np.vstack((xs_hat, xt_hat))

        kmeans = KMeans(n_clusters=n_cluster, random_state=42, n_init='auto') # Added n_init='auto' to avoid warning
        predicted_labels = kmeans.fit_predict(x_comb)
        sil = None
        ari = adjusted_rand_score(self.reallabel, predicted_labels[ns:])
        sil = silhouette_score(x_comb, predicted_labels)

        ariT = None
        silT = None
        # kmean2 = KMeans(n_clusters=n_cluster, random_state=42)
        # pre_label_onlyT = kmean2.fit_predict(xt_hat)
        # ariT = adjusted_rand_score(self.reallabel, pre_label_onlyT)
        # silT = silhouette_score(xt_hat, pre_label_onlyT)
        return {
            "epoch": epoch,
            "ari_comb": ari,
            "silhouette_comb": sil,
            "ari_Tonly": ariT,
            "sil_Tonly": silT,
        }
    def check_silhoutte(
            self,
            Xs,
            Xt,
            epoch,
            n_cluster:int =2,
            ) -> Dict[str, Any]:

        ns = len(Xs)
        xs_hat = self.extract_feature(Xs.tensors[0].to(self.device))
        xt_hat = self.extract_feature(Xt.tensors[0].to(self.device))
        xs_hat = xs_hat.cpu().numpy()
        xt_hat = xt_hat.cpu().numpy()

        x_comb = np.vstack((xs_hat, xt_hat))

        kmeans = KMeans(n_clusters=n_cluster, random_state=42, n_init='auto') # Added n_init='auto' to avoid warning
        predicted_labels = kmeans.fit_predict(x_comb)

        sil = silhouette_score(x_comb, predicted_labels)

        return {
            "epoch": epoch,
            "silhouette_comb": sil,
        }

    def compute_gradient_penalty(
            self, 
            source_data: torch.Tensor, 
            target_data: torch.Tensor
            ) -> torch.Tensor:
        
        alpha = torch.rand(source_data.size(0), 1).to(self.device)

        # In WDGRL, the interpolation is between the feature embeddings
        # Assuming source_data and target_data are already features, which they are 
        # when called from train, but the original code was:
        # source_features = self.encoder(source_data)
        # target_features = self.encoder(target_data)
        # ... and then passed here. So let's stick to using the feature names:
        # The tensors passed here are the *features*.
        source_features = source_data
        target_features = target_data

        differences = target_features - source_features
        interpolates = source_features + (alpha * differences)
        
        # The original code used a stack of three tensors, but WDGRL with Gradient Penalty 
        # usually only requires the interpolated one for the GP calculation
        # and the endpoints (source/target) for the Wasserstein distance.
        # Since the interpolation is linear, the max norm of the gradient is at 
        # the interpolated points (ideally).

        # For correctness with the original code structure:
        # The stack is used here only to pass the interpolated points to the critic. 
        # The original code's `interpolates` variable is the 3-stacked tensor.
        interpolates_for_critic = torch.stack([interpolates, source_features, target_features])

        # Ensure the stacked tensor has gradient tracking for the backward pass
        interpolates_for_critic.requires_grad_()

        preds = self.critic(interpolates_for_critic)
        
        # Compute the gradients of the critic output w.r.t the input features
        gradients = torch.autograd.grad(
            preds, 
            interpolates_for_critic,
            grad_outputs=torch.ones_like(preds),
            retain_graph=True, 
            create_graph=True
        )[0]
        
        # Only take the gradient of the interpolated points (the first in the stack)
        gradients_for_gp = gradients[0, :, :] 

        # The gradient penalty is computed on the interpolated points
        # The second dimension (dim=1) is the feature dimension
        gradient_norm = gradients_for_gp.norm(2, dim=1)
        gradient_penalty = ((gradient_norm - 1)**2).mean()
        return gradient_penalty

    def train(
            self, 
            source_dataset: TensorDataset, 
            target_dataset: TensorDataset, 
            num_epochs: int = 100, 
            gamma: float = 1.0,
            dc_iter: int = 5,
            batch_size: int = 32,
            verbose: bool = False,
            early_stopping: bool = False,
            model_path: str = None,
            check_ari: bool = True,
            ) -> Dict[str, List[float]]:
        
        self.encoder.train()
        self.critic.train()
        losses = []
        source_critic_scores = []
        target_critic_scores = []
        
        source_size = len(source_dataset)
        target_size = len(target_dataset)

        best_silhoutte = -float('inf')
        log_ari = []
        
        for epoch in trange(num_epochs, desc='Epoch'):


            epoch_wasserstein_distance_avg = 0.0 # To track the average Wasserstein distance over dc_iter for scheduler
            
            # --- Training Loop ---
            loss = 0
            # for source_data, target_data in zip(source_loader, target_loader):
            
            # Randomly sample m from source
            source_indices = torch.randint(0, source_size, (batch_size,))
            source_batch = torch.stack([source_dataset[i][0] for i in source_indices])

            # Randomly sample m from target (with replacement if smaller)
            target_indices = torch.randint(0, target_size, (batch_size,))
            target_batch = torch.stack([target_dataset[i][0] for i in target_indices])

            source_data, target_data = source_batch.to(self.device), target_batch.to(self.device)

            # Train domain critic
            for _ in range(dc_iter):
                self.critic_optimizer.zero_grad()
                
                with torch.no_grad():
                    source_features = self.encoder(source_data).view(source_data.size(0), -1)
                    target_features = self.encoder(target_data).view(target_data.size(0), -1)
                
                # Compute empirical Wasserstein distance
                dc_source = self.critic(source_features)
                dc_target = self.critic(target_features)
                wasserstein_distance = (dc_source.mean() - dc_target.mean())

                # Gradient penalty
                # The features are passed here for interpolation
                gradient_penalty = self.compute_gradient_penalty(source_features, target_features)

                # Domain critic loss
                # Critic loss is the negative of the objective: max_D [D(X_s) - D(X_t) - GP]
                dc_loss = - wasserstein_distance + gamma * gradient_penalty 
                dc_loss.backward()
                self.critic_optimizer.step()

                epoch_wasserstein_distance_avg += wasserstein_distance.item()
            
            # Train feature extractor (Encoder)
            self.encoder_optimizer.zero_grad()
            source_features = self.encoder(source_data)
            target_features = self.encoder(target_data)

            dc_source = self.critic(source_features)
            dc_target = self.critic(target_features)

            # Encoder objective: min_G [D(X_s) - D(X_t)] -> Encoder wants to reduce this distance
            wasserstein_distance = (dc_source.mean() - dc_target.mean())
            
            objective_function = wasserstein_distance

            objective_function.backward()
            self.encoder_optimizer.step()

            loss += objective_function.item()
            epoch_wasserstein_distance_avg /= dc_iter # Average W-distance after critic updates

            # Step the Learning Rate Scheduler (NEW)
            if self.reduce_lr_on:
                # We use the encoder's objective (the W-distance) as the metric to track.
                # Since the encoder MINIMIZES this, we track for 'min' mode in the scheduler.
                self.encoder_scheduler.step(objective_function.item())
                
                # The critic's objective is to MAXIMIZE W_distance, but its loss is -W_distance + GP.
                # To use the same metric (W-distance) for the critic scheduler, we pass the 
                # negative of the average W-distance after the critic steps, as the critic
                # attempts to MAXIMIZE W-distance (minimize -W-distance).
                # We use -epoch_wasserstein_distance_avg for the 'min' mode scheduler to step.
                self.critic_scheduler.step(-epoch_wasserstein_distance_avg) 

            # --- Logging and Checkpoints ---
            if check_ari and (epoch%100==0 or epoch == num_epochs - 1): # Check on last epoch too
                log_ari.append(self.check_metric(source_dataset, target_dataset,epoch=epoch, n_cluster=self.n_clusters))
            
            if early_stopping and epoch > num_epochs//2 and epoch%100==0:
                sil = self.check_silhoutte(source_dataset, target_dataset,epoch=epoch, n_cluster=self.n_clusters)["silhouette_comb"]
                if sil > best_silhoutte:
                    best_silhoutte = sil
                    self.save_model(f"{model_path}/early_model")
                    if check_ari:
                        print("temp model save with ari = ", log_ari[-1]["ari_comb"])


            losses.append(loss)
            if verbose:
                print(f'Epoch {epoch + 1}/{num_epochs} | Encoder Objective (W-Dist): {objective_function.item():.6f}')

        return {
            "loss": losses,
            "log_ari": log_ari,
            }
    
    @torch.no_grad()
    def extract_feature(
        self, 
        x: torch.Tensor
        ) -> torch.Tensor:

        self.encoder.eval()
        return self.encoder(x.to(self.device))
    
    @torch.no_grad()
    def criticize(self, x: torch.Tensor) -> float:
        self.encoder.eval()
        self.critic.eval()
        return self.critic(self.encoder(x.to(self.device))).mean().item()
    
    
    def save_model(self, folder_path: str):
        """Save encoder and critic into the given folder."""
        os.makedirs(folder_path, exist_ok=True)

        torch.save(self.encoder.state_dict(), os.path.join(folder_path, "encoder.pth"))
        torch.save(self.critic.state_dict(), os.path.join(folder_path, "critic.pth"))

        print(f"Encoder and Critic saved to {folder_path}")

    def load_model(self, folder_path: str):
        """Load encoder and critic from the given folder."""
        encoder_path = os.path.join(folder_path, "encoder.pth")
        critic_path = os.path.join(folder_path, "critic.pth")

        self.encoder.load_state_dict(torch.load(encoder_path, map_location=self.device))
        self.critic.load_state_dict(torch.load(critic_path, map_location=self.device))

        print(f"Encoder and Critic loaded from {folder_path}")