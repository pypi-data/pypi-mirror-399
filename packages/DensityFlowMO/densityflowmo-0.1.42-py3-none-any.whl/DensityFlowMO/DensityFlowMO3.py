import pyro
import pyro.distributions as dist
from pyro.optim import ExponentialLR
from pyro.infer import SVI, JitTraceEnum_ELBO, TraceEnum_ELBO, config_enumerate

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.distributions.utils import logits_to_probs, probs_to_logits, clamp_probs
from torch.distributions import constraints
from torch.distributions.transforms import SoftmaxTransform

from .utils.custom_mlp import MLP, Exp, ZeroBiasMLP, ZeroBiasMLP2, ZeroBiasMLP3
from .utils.utils import CustomDataset, CustomDataset2, CustomDataset3, tensor_to_numpy, convert_to_tensor

from .dist.negbinomial import NegativeBinomial as MyNB
from .dist.negbinomial import ZeroInflatedNegativeBinomial as MyZINB

from DensityFlow import DensityFlow

import zuko 
from pyro.contrib.zuko import ZukoToPyro

import os
import argparse
import random
import numpy as np
import datatable as dt
from tqdm import tqdm
from scipy import sparse

import scanpy as sc
from .atac import binarize

from typing import Literal

import warnings
warnings.filterwarnings("ignore")

import dill as pickle
import gzip
from packaging.version import Version
torch_version = torch.__version__


def set_random_seed(seed):
    # Set seed for PyTorch
    torch.manual_seed(seed)
    
    # If using CUDA, set the seed for CUDA
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)  # For multi-GPU setups.
    
    # Set seed for NumPy
    np.random.seed(seed)
    
    # Set seed for Python's random module
    random.seed(seed)

    # Set seed for Pyro
    pyro.set_rng_seed(seed)

class DensityFlowMO3(nn.Module):
    """DensityFlowMO3 model

    Parameters
    ----------
    input_size : int
        Number of features like genes or peaks

    codebook_size: int
        Number of codebook items

    perturb_size: int
        Number of perturbations 
        
    cov_size: int
        Number of covariates

    z_dim : int
        Dimensionality of latent space.

    z_dist: str
        Distribution model of latent variable. One of 'normal', 'studentt', 'laplacian',
        'cauchy', and 'gumbel'. Default is 'studentt'.
        
    loss_func: str
        Distribution model for observed profiles. One of 'negbinomial', 'poisson', 'multinomial',
        'bernoulli'. Default is 'poisson'


    Examples
    --------
    >>> from DensityFlowMO3 import DensityFlowMO3
    >>> from DensityFlowMO3.perturb import LabelMatrix
    >>> import scanpy as sc
    >>> adata = sc.read('dataset.h5ad')
    >>> adata.X = adata.layers['counts].copy()
    >>> sc.pp.normalize_total(adata)
    >>> sc.pp.log1p(adata)
    >>> xs = adata.X 
    >>> lb = LabelMatrix()
    >>> us = lb.fit_transform(adata_train.obs[pert_col], control_label=control_label)
    >>> ln = lb.labels_
    >>> model = DensityFlowMO3(input_size = xs.shape[1],
                            perturb_size=us.shape[1],
                            use_cuda=True)
    >>> model.fit(xs, us=us, use_jax=True)
    >>> zs_basal = model.get_basal_embedding(xs)
    >>> zs_complete = model.get_complete_embedding(xs, us)
    """
    def __init__(self,
                 rna_dim: int,
                 atac_dim: int,
                 codebook_size: int = 15,
                 perturb_size: int = 0,
                 perturb_classes: int = 0,
                 cov_size: int = 0,
                 transforms: int = 3,
                 z_dim: int = 50,
                 z_dist: Literal['normal','studentt','laplacian','cauchy','gumbel'] = 'studentt',
                 rna_loss_func: Literal['negbinomial','poisson','multinomial','bernoulli'] = 'poisson',
                 atac_loss_func: Literal['negbinomial','poisson','multinomial','bernoulli'] = 'multinomial',
                 dispersion: float = 10.0,
                 use_zeroinflate: bool = False,
                 hidden_layers: list = [512],
                 hidden_layer_activation: Literal['relu','softplus','leakyrelu','linear'] = 'relu',
                 flow_hidden_layers: list = [128,128],
                 nn_dropout: float = 0.1,
                 post_layer_fct: list = ['layernorm'],
                 post_act_fct: list = None,
                 config_enum: str = 'parallel',
                 use_cuda: bool = True,
                 seed: int = 42,
                 dtype = torch.float32, # type: ignore
                 ):
        super().__init__()

        self.latent_dim = z_dim
        self.use_cuda = use_cuda
        self.transforms = transforms
        self.flow_hidden_layers = flow_hidden_layers
        self.rna_loss_func = rna_loss_func
        self.atac_loss_func = atac_loss_func
        self.dtype = dtype
                
        print('#### RNA ####')
        self.rna_perturb_model = DensityFlow(input_dim=rna_dim,
                                                 perturb_size=perturb_size,
                                                 perturb_classes=perturb_classes,
                                                 cov_size=cov_size,
                                                 z_dim=z_dim,
                                                 z_dist=z_dist,
                                                 loss_func=rna_loss_func,
                                                 dispersion=dispersion,
                                                 use_zeroinflate=use_zeroinflate,
                                                 hidden_layers=hidden_layers,
                                                 hidden_layer_activation=hidden_layer_activation,
                                                 nn_dropout=nn_dropout,
                                                 post_layer_fct=post_layer_fct,
                                                 post_act_fct=post_act_fct,
                                                 config_enum=config_enum,
                                                 use_cuda=use_cuda,
                                                 seed=seed,
                                                 dtype=dtype
                                                 )
        print('#### ATAC ####')
        self.atac_perturb_model = DensityFlow(input_dim=atac_dim,
                                                 perturb_size=perturb_size,
                                                 perturb_classes=perturb_classes,
                                                 cov_size=cov_size,
                                                 codebook_size=codebook_size,
                                                 z_dim=z_dim,
                                                 z_dist=z_dist,
                                                 loss_func=atac_loss_func,
                                                 dispersion=dispersion,
                                                 use_zeroinflate=use_zeroinflate,
                                                 hidden_layers=hidden_layers,
                                                 hidden_layer_activation=hidden_layer_activation,
                                                 nn_dropout=nn_dropout,
                                                 post_layer_fct=post_layer_fct,
                                                 post_act_fct=post_act_fct,
                                                 config_enum=config_enum,
                                                 use_cuda=use_cuda,
                                                 seed=seed,
                                                 dtype=dtype
                                                 )

        self.seed = seed
        set_random_seed(seed)
        self.setup_networks()

    def setup_networks(self):
        self.decoder_state_atac2rna = zuko.flows.NSF(features=self.latent_dim, context=self.latent_dim, transforms=self.transforms, hidden_features=self.flow_hidden_layers)
        self.decoder_state_rna2atac = zuko.flows.NSF(features=self.latent_dim, context=self.latent_dim, transforms=self.transforms, hidden_features=self.flow_hidden_layers)
        
        self.decoder_perturb_atac2rna = zuko.flows.NSF(features=self.latent_dim, context=self.latent_dim, transforms=self.transforms, hidden_features=self.flow_hidden_layers)
        self.decoder_perturb_rna2atac = zuko.flows.NSF(features=self.latent_dim, context=self.latent_dim, transforms=self.transforms, hidden_features=self.flow_hidden_layers)
            
        if self.use_cuda:
            self.cuda()

    def get_device(self):
        return next(self.parameters()).device

    def cutoff(self, xs, thresh=None):
        eps = torch.finfo(xs.dtype).eps
        
        if not thresh is None:
            if eps < thresh:
                eps = thresh

        xs = xs.clamp(min=eps)

        if torch.any(torch.isnan(xs)):
            xs[torch.isnan(xs)] = eps

        return xs

    def softmax(self, xs):
        #xs = SoftmaxTransform()(xs)
        xs = dist.Multinomial(total_count=1, logits=xs).mean
        return xs
    
    def sigmoid(self, xs):
        #sigm_enc = nn.Sigmoid()
        #xs = sigm_enc(xs)
        #xs = clamp_probs(xs)
        xs = dist.Bernoulli(logits=xs).mean
        return xs

    def softmax_logit(self, xs):
        eps = torch.finfo(xs.dtype).eps
        xs = self.softmax(xs)
        xs = torch.logit(xs, eps=eps)
        return xs

    def logit(self, xs):
        eps = torch.finfo(xs.dtype).eps
        xs = torch.logit(xs, eps=eps)
        return xs

    def dirimulti_param(self, xs):
        xs = self.dirimulti_mass * self.sigmoid(xs)
        return xs

    def multi_param(self, xs):
        xs = self.softmax(xs)
        return xs
            
    def cross_model(self, rna_ns_zs, rna_shifts, atac_ns_zs, atac_shifts):
        pyro.module('DensityFlowMO3', self)

        with pyro.plate('data'):
            ###############################################################
            # RNA 
            _ = pyro.sample('atac2rna_zs', ZukoToPyro(self.decoder_state_atac2rna(atac_ns_zs)), obs=rna_ns_zs)
            _ = pyro.sample('atac2rna_dzs', ZukoToPyro(self.decoder_perturb_atac2rna(atac_shifts)), obs=rna_shifts)

            ###############################################################
            # atac 
            _ = pyro.sample('rna2atac_zs', ZukoToPyro(self.decoder_state_rna2atac(rna_ns_zs)), obs=atac_ns_zs)
            _ = pyro.sample('rna2atac_dzs', ZukoToPyro(self.decoder_perturb_rna2atac(rna_shifts)), obs=atac_shifts)
                    
    def cross_guide(self, rna_ns_zs, rna_shifts, atac_ns_zs, atac_shifts):
        pass
    
    def _total_rna_effects(self, rna_zs, us, ts):
        zus = self.rna_perturb_model._total_effects(rna_zs, us, ts)
        return zus
    
    def _total_atac_effects(self, atac_zs, us, ts):
        zus = self.atac_perturb_model._total_effects(atac_zs, us, ts)
        return zus
                        
    def _get_codebook_identity(self):
        return torch.eye(self.code_size, **self.options)
    
    def _get_rna_codebook(self):
        cb = self.rna_perturb_model._get_codebook()
        return cb
    
    def get_rna_codebook(self):
        """
        Return the mean part of metacell codebook
        """
        cb = self._get_rna_codebook()
        cb = tensor_to_numpy(cb)
        return cb

    def _rna_codebook_map(self, xs_rna, soft_assign):
        if soft_assign:
            ns = self._rna_soft_assignments(xs_rna)
        else:
            ns = self._rna_hard_assignments(xs_rna)
        cb = self._get_rna_codebook()
        zs = torch.matmul(ns, cb)
        return zs
    
    def rna_codebook_map(self, xs_rna, soft_assign: bool=True, batch_size:int=1024, show_progress=True):
        xs_rna = self.preprocess(xs_rna,'rna')
        xs_rna = convert_to_tensor(xs_rna, device='cpu')
        dataset = CustomDataset(xs_rna)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        Z = []
        with tqdm(total=len(dataloader), disable=not show_progress, desc='', unit='batch') as pbar:
            for X_batch, _ in dataloader:
                X_batch = X_batch.to(self.get_device())
                zns = self._rna_codebook_map(X_batch, soft_assign)
                Z.append(tensor_to_numpy(zns))
                pbar.update(1)

        Z = np.concatenate(Z)
        return Z
    
    def _get_atac_codebook(self):
        cb = self.atac_perturb_model._get_codebook()
        return cb
    
    def get_atac_codebook(self):
        """
        Return the mean part of metacell codebook
        """
        cb = self._get_atac_codebook()
        cb = tensor_to_numpy(cb)
        return cb

    def _atac_codebook_map(self, xs_atac, soft_assign):
        if soft_assign:
            ns = self._atac_soft_assignments(xs_atac)
        else:
            ns = self._atac_hard_assignments(xs_atac)
        cb = self._get_rna_codebook()
        zs = torch.matmul(ns, cb)
        return zs
    
    def atac_codebook_map(self, xs_atac, soft_assign: bool=True, batch_size:int=1024, show_progress=True):
        xs_atac = self.preprocess(xs_atac,'atac')
        xs_atac = convert_to_tensor(xs_atac, device='cpu')
        dataset = CustomDataset(xs_atac)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        Z = []
        with tqdm(total=len(dataloader), disable=not show_progress, desc='', unit='batch') as pbar:
            for X_batch, _ in dataloader:
                X_batch = X_batch.to(self.get_device())
                zns = self._atac_codebook_map(X_batch, soft_assign)
                Z.append(tensor_to_numpy(zns))
                pbar.update(1)

        Z = np.concatenate(Z)
        return Z
    
    def _get_rna_complete_embedding(self, xs_rna, us):
        basal,_ = self._get_rna_basal_embedding(xs_rna)
        dzs = self._total_rna_effects(basal, us)
        return basal + dzs 
    
    def get_rna_complete_embedding(self, xs_rna, us, batch_size:int=1024, show_progress=True):
        xs_rna = self.preprocess(xs_rna,'rna')
        xs_rna = convert_to_tensor(xs_rna, device='cpu')
        us = convert_to_tensor(us, device='cpu')
        dataset = CustomDataset(xs_rna)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        Z = []
        with tqdm(total=len(dataloader), disable=not show_progress, desc='', unit='batch') as pbar:
            for X_batch, idx in dataloader:
                X_batch = X_batch.to(self.get_device())
                U_batch = us[idx].to(self.get_device())
                zns = self._get_rna_complete_embedding(X_batch, U_batch)
                Z.append(tensor_to_numpy(zns))
                pbar.update(1)

        Z = np.concatenate(Z)
        return Z
    
    def _get_atac_complete_embedding(self, xs_atac, us):
        basal,_ = self._get_atac_basal_embedding(xs_atac)
        dzs = self._total_atac_effects(basal, us)
        return basal + dzs 
    
    def get_atac_complete_embedding(self, xs_atac, us, batch_size:int=1024, show_progress=True):
        xs_atac = self.preprocess(xs_atac,'atac')
        xs_atac = convert_to_tensor(xs_atac, device='cpu')
        us = convert_to_tensor(us, device='cpu')
        dataset = CustomDataset(xs_atac)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        Z = []
        with tqdm(total=len(dataloader), disable=not show_progress, desc='', unit='batch') as pbar:
            for X_batch, idx in dataloader:
                X_batch = X_batch.to(self.get_device())
                U_batch = us[idx].to(self.get_device())
                zns = self._get_atac_complete_embedding(X_batch, U_batch)
                Z.append(tensor_to_numpy(zns))
                pbar.update(1)

        Z = np.concatenate(Z)
        return Z

    def _get_rna_basal_embedding(self, xs_rna):           
        loc = self.rna_perturb_model._get_basal_embedding(xs_rna)
        return loc
    
    def _get_atac_basal_embedding(self, xs_atac):           
        loc = self.atac_perturb_model._get_basal_embedding(xs_atac)
        return loc
    
    def get_rna_basal_embedding(self, 
                             xs_rna, 
                             batch_size: int = 1024,
                             show_progress=True):
        """
        Return cells' basal latent representations

        Parameters
        ----------
        xs: numpy.array
            Single-cell expression matrix. It should be a Numpy array or a Pytorch Tensor
        batch_size: int
            Size of batch processing
        show_progress: bool
            Verbose on or off
        """
        xs_rna = self.preprocess(xs_rna,'rna')
        xs_rna = convert_to_tensor(xs_rna, device='cpu')
        dataset = CustomDataset(xs_rna)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        Z = []
        with tqdm(total=len(dataloader), disable=not show_progress, desc='', unit='batch') as pbar:
            for X_batch, _ in dataloader:
                X_batch = X_batch.to(self.get_device())
                zns = self._get_rna_basal_embedding(X_batch)
                Z.append(tensor_to_numpy(zns))
                pbar.update(1)

        Z = np.concatenate(Z)
        return Z
    
    def get_atac_basal_embedding(self, 
                             xs_atac, 
                             batch_size: int = 1024,
                             show_progress=True):
        """
        Return cells' basal latent representations

        Parameters
        ----------
        xs: numpy.array
            Single-cell expression matrix. It should be a Numpy array or a Pytorch Tensor
        batch_size: int
            Size of batch processing
        show_progress: bool
            Verbose on or off
        """
        xs_atac = self.preprocess(xs_atac,'atac')
        xs_atac = convert_to_tensor(xs_atac, device='cpu')
        dataset = CustomDataset(xs_atac)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        Z = []
        with tqdm(total=len(dataloader), disable=not show_progress, desc='', unit='batch') as pbar:
            for X_batch, _ in dataloader:
                X_batch = X_batch.to(self.get_device())
                zns = self._get_atac_basal_embedding(X_batch)
                Z.append(tensor_to_numpy(zns))
                pbar.update(1)

        Z = np.concatenate(Z)
        return Z
    
    def _rna_code(self, xs_rna):
        alpha = self.rna_perturb_model._code(xs_rna)
        return alpha
    
    def rna_code(self, xs_rna, batch_size=1024, show_progress=True):
        xs_rna = self.preprocess(xs_rna,'rna')
        xs_rna = convert_to_tensor(xs_rna, device='cpu')
        dataset = CustomDataset(xs_rna)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        A = []
        with tqdm(total=len(dataloader), disable=not show_progress, desc='', unit='batch') as pbar:
            for X_batch, _ in dataloader:
                X_batch = X_batch.to(self.get_device())
                a = self._rna_code(X_batch)
                A.append(tensor_to_numpy(a))
                pbar.update(1)

        A = np.concatenate(A)
        return A
    
    def _atac_code(self, xs_atac):
        alpha = self.atac_perturb_model._code(xs_atac)
        return alpha
    
    def atac_code(self, xs_atac, batch_size=1024, show_progress=True):
        xs_atac = self.preprocess(xs_atac,'atac')
        xs_atac = convert_to_tensor(xs_atac, device='cpu')
        dataset = CustomDataset(xs_atac)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        A = []
        with tqdm(total=len(dataloader), disable=not show_progress, desc='', unit='batch') as pbar:
            for X_batch, _ in dataloader:
                X_batch = X_batch.to(self.get_device())
                a = self._atac_code(X_batch)
                A.append(tensor_to_numpy(a))
                pbar.update(1)

        A = np.concatenate(A)
        return A
    
    def _rna_soft_assignments(self, xs_rna):
        alpha = self._rna_code(xs_rna)
        alpha = self.softmax(alpha)
        return alpha
    
    def rna_soft_assignments(self, xs_rna, batch_size=1024, show_progress=True):
        """
        Map cells to metacells and return the probabilistic values of metacell assignments
        """
        xs_rna = self.preprocess(xs_rna,'rna')
        xs_rna = convert_to_tensor(xs_rna, device='cpu')
        dataset = CustomDataset(xs_rna)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        A = []
        with tqdm(total=len(dataloader), disable=not show_progress, desc='', unit='batch') as pbar:
            for X_batch, _ in dataloader:
                X_batch = X_batch.to(self.get_device())
                a = self._rna_soft_assignments(X_batch)
                A.append(tensor_to_numpy(a))
                pbar.update(1)

        A = np.concatenate(A)
        return A
    
    def _atac_soft_assignments(self, xs_atac):
        alpha = self._atac_code(xs_atac)
        alpha = self.softmax(alpha)
        return alpha
    
    def atac_soft_assignments(self, xs_atac, batch_size=1024, show_progress=True):
        """
        Map cells to metacells and return the probabilistic values of metacell assignments
        """
        xs_atac = self.preprocess(xs_atac,'atac')
        xs_atac = convert_to_tensor(xs_atac, device='cpu')
        dataset = CustomDataset(xs_atac)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        A = []
        with tqdm(total=len(dataloader), disable=not show_progress, desc='', unit='batch') as pbar:
            for X_batch, _ in dataloader:
                X_batch = X_batch.to(self.get_device())
                a = self._atac_soft_assignments(X_batch)
                A.append(tensor_to_numpy(a))
                pbar.update(1)

        A = np.concatenate(A)
        return A
    
    def _rna_hard_assignments(self, xs_rna):
        alpha = self._rna_code(xs_rna)
        res, ind = torch.topk(alpha, 1)
        ns = torch.zeros_like(alpha).scatter_(1, ind, 1.0)
        return ns
    
    def rna_hard_assignments(self, xs_rna, batch_size=1024, show_progress=True):
        """
        Map cells to metacells and return the assigned metacell identities.
        """
        xs_rna = self.preprocess(xs_rna,'rna')
        xs_rna = convert_to_tensor(xs_rna, device='cpu')
        dataset = CustomDataset(xs_rna)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        A = []
        with tqdm(total=len(dataloader), disable=not show_progress, desc='', unit='batch') as pbar:
            for X_batch, _ in dataloader:
                X_batch = X_batch.to(self.get_device())
                a = self._rna_hard_assignments(X_batch)
                A.append(tensor_to_numpy(a))
                pbar.update(1)

        A = np.concatenate(A)
        return A
    
    def _atac_hard_assignments(self, xs_atac):
        alpha = self._rna_code(xs_atac)
        res, ind = torch.topk(alpha, 1)
        ns = torch.zeros_like(alpha).scatter_(1, ind, 1.0)
        return ns
    
    def atac_hard_assignments(self, xs_atac, batch_size=1024, show_progress=True):
        """
        Map cells to metacells and return the assigned metacell identities.
        """
        xs_atac = self.preprocess(xs_atac,'atac')
        xs_atac = convert_to_tensor(xs_atac, device='cpu')
        dataset = CustomDataset(xs_atac)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        A = []
        with tqdm(total=len(dataloader), disable=not show_progress, desc='', unit='batch') as pbar:
            for X_batch, _ in dataloader:
                X_batch = X_batch.to(self.get_device())
                a = self._atac_hard_assignments(X_batch)
                A.append(tensor_to_numpy(a))
                pbar.update(1)

        A = np.concatenate(A)
        return A
    
    def rna_predict(self, xs_rna, perturb, perturb_type, library_sizes=None, show_progress=True):
        counts, log_mu = self.rna_perturb_model.predict(xs_rna, perturb, perturb_type, library_sizes, show_progress)
        return counts, log_mu
    
    def atac_predict(self, xs_atac, perturb, perturb_type, library_sizes=None, show_progress=True):
        counts, log_mu = self.atac_perturb_model.predict(xs_atac, perturb, perturb_type, library_sizes, show_progress)
        return counts, log_mu
    
    def _rna_cell_shift(self, rna_zs, perturb, perturb_type):
        ms = self.rna_perturb_model._cell_shift(rna_zs, perturb, perturb_type)
        return ms 
    
    def _atac_cell_shift(self, atac_zs, perturb, perturb_type):
        ms = self.rna_perturb_model._cell_shift(atac_zs, perturb, perturb_type)
        return ms 

    def get_rna_cell_shift(self, 
                             xs_rna, 
                             perturb_us,
                             perturb_type, 
                             use_codebook: bool = True,
                             soft_assign: bool = True,
                             batch_size: int = 1024,
                             show_progress=True):
        """
        Compute displacement vector induced by a perturbation.
        
        Parameters
        ----------
        xs: numpy.array
            single-cell matrix
            
        perturb_us: numpy.array
            perturbation information for cells

        soft_assign: bool
            use similarity to all codebook items for prediction or rely on the information
            from the most similar codebook item.
            
        batch_size: int
            size of batch processing
            
        show_progress: bool
            verbose on or off
        """
        #xs = self.preprocess(xs)
        if use_codebook:
            zs = self.rna_codebook_map(xs_rna, soft_assign=soft_assign, show_progress=show_progress)
        else:
            zs = self.get_rna_basal_embedding(xs_rna, show_progress=show_progress)
        zs = convert_to_tensor(zs, device='cpu')
        ps = convert_to_tensor(perturb_us, device='cpu')
        ts = convert_to_tensor(perturb_type, device='cpu')
        dataset = CustomDataset(zs)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        Z = []
        with tqdm(total=len(dataloader), disable=not show_progress, desc='', unit='batch') as pbar:
            for Z_batch, idx in dataloader:
                Z_batch = Z_batch.to(self.get_device())
                P_batch = ps[idx].to(self.get_device())
                T_batch = ts[idx].to(self.get_device())
                zns = self._rna_cell_shift(Z_batch, P_batch, T_batch)
                Z.append(tensor_to_numpy(zns))
                pbar.update(1)

        Z = np.concatenate(Z)
        return Z
    
    def get_atac_cell_shift(self, 
                             xs_atac, 
                             perturb_us,
                             perturb_type,
                             use_codebook: bool = True,
                             soft_assign: bool = True,
                             batch_size: int = 1024,
                             show_progress=True):
        """
        Compute displacement vector induced by a perturbation.
        
        Parameters
        ----------
        xs: numpy.array
            single-cell matrix
            
        perturb_us: numpy.array
            perturbation information for cells

        soft_assign: bool
            use similarity to all codebook items for prediction or rely on the information
            from the most similar codebook item.
            
        batch_size: int
            size of batch processing
            
        show_progress: bool
            verbose on or off
        """
        #xs = self.preprocess(xs)
        if use_codebook:
            zs = self.atac_codebook_map(xs_atac, soft_assign=soft_assign, show_progress=show_progress)
        else:
            zs = self.get_atac_basal_embedding(xs_atac, show_progress=show_progress)
        zs = convert_to_tensor(zs, device='cpu')
        ps = convert_to_tensor(perturb_us, device='cpu')
        ts = convert_to_tensor(perturb_type, device='cpu')
        dataset = CustomDataset(zs)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        Z = []
        with tqdm(total=len(dataloader), disable=not show_progress, desc='', unit='batch') as pbar:
            for Z_batch, idx in dataloader:
                Z_batch = Z_batch.to(self.get_device())
                P_batch = ps[idx].to(self.get_device())
                T_batch = ts[idx].to(self.get_device())
                zns = self._atac_cell_shift(Z_batch, P_batch, T_batch)
                Z.append(tensor_to_numpy(zns))
                pbar.update(1)

        Z = np.concatenate(Z)
        return Z
    
    def _rna_log_mu(self, zs):
        return self.rna_perturb_model._log_mu(zs)
    
    def _atac_log_mu(self, zs):
        return self.atac_perturb_model._log_mu(zs)
    
    def get_rna_log_mu(self, zs, batch_size: int = 1024, show_progress=True):
        """
        Return cells' changes in the feature space induced by specific perturbation of a factor

        """
        zs = convert_to_tensor(zs, device='cpu')
        dataset = CustomDataset(zs)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        R = []
        with tqdm(total=len(dataloader), disable=not show_progress, desc='', unit='batch') as pbar:
            for Z_batch, _ in dataloader:
                Z_batch = Z_batch.to(self.get_device())
                r = self._rna_log_mu(Z_batch)
                R.append(tensor_to_numpy(r))
                pbar.update(1)

        R = np.concatenate(R)
        return R
    
    def get_atac_log_mu(self, zs, batch_size: int = 1024, show_progress=True):
        """
        Return cells' changes in the feature space induced by specific perturbation of a factor

        """
        zs = convert_to_tensor(zs, device='cpu')
        dataset = CustomDataset(zs)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        R = []
        with tqdm(total=len(dataloader), disable=not show_progress, desc='', unit='batch') as pbar:
            for Z_batch, _ in dataloader:
                Z_batch = Z_batch.to(self.get_device())
                r = self._atac_log_mu(Z_batch)
                R.append(tensor_to_numpy(r))
                pbar.update(1)

        R = np.concatenate(R)
        return R
    
    def _count(self, modality, log_mu, library_size=None):
        if modality=='rna':
            counts = self.rna_perturb_model._count(log_mu, library_size)
        if modality=='atac':
            counts = self.atac_perturb_model._count(log_mu, library_size)
        return counts
    
    def get_counts(self, modality, zs, library_sizes, batch_size: int = 1024, show_progress=True):
        '''
        Generate observational profiles from latent states.
        
        Parameters
        ----------
        zs: numpy.array
            latent states for cells
            
        library_sizes: numpy.array
            library sizes for cells
            
        batch_size: int
            size of batch processing
            
        show_progress: bool
            verbose on or off
        '''

        zs = convert_to_tensor(zs, device='cpu')
        
        if type(library_sizes) == list:
            library_sizes = np.array(library_sizes).reshape(-1,1)
        elif len(library_sizes.shape)==1:
            library_sizes = library_sizes.reshape(-1,1)
        ls = convert_to_tensor(library_sizes, device='cpu')
        
        dataset = CustomDataset(zs)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)
        
        E = []
        with tqdm(total=len(dataloader), disable=not show_progress, desc='', unit='batch') as pbar:
            for Z_batch, idx in dataloader:
                Z_batch = Z_batch.to(self.get_device())
                L_batch = ls[idx].to(self.get_device())
                if modality=='rna':
                    log_mu = self._rna_log_mu(Z_batch)
                else:
                    log_mu = self._atac_log_mu(Z_batch)
                counts = self._count(modality, log_mu, L_batch)
                E.append(tensor_to_numpy(counts))
                pbar.update(1)
        
        E = np.concatenate(E)
        return E
    
    def preprocess(self, xs, modality, threshold=0):
        if modality=='rna':
            loss_func = self.rna_loss_func
        if modality=='atac':
            loss_func = self.atac_loss_func
            
        if loss_func == 'bernoulli':
            ad = sc.AnnData(xs)
            binarize(ad, threshold=threshold)
            xs = ad.X.copy()
        elif loss_func in ['poisson','multinomial']:
            xs = np.round(xs)
            
        if sparse.issparse(xs):
            xs = xs.toarray()
        return xs 
    
    def fit(self, 
            xs_paired_dict, 
            xs_rna_unpaired_list = None,
            xs_atac_unpaired_list = None,
            us = None, 
            ts = None,
            cs = None,
            num_epochs: int = 100, 
            learning_rate: float = 0.0001, 
            batch_size: int = 256, 
            algo: Literal['adam','rmsprop','adamw'] = 'adam', 
            beta_1: float = 0.9, 
            weight_decay: float = 0.005, 
            decay_rate: float = 0.9,
            config_enum: str = 'parallel',
            threshold: int = 0,
            use_jax: bool = False,
            show_progress=True):
        """
        Train the DensityFlowMO3 model.

        Parameters
        ----------
        xs: numpy.array
            Single-cell experssion matrix. It should be a Numpy array or a Pytorch Tensor. Rows are cells and columns are features.
        us: numpy.array
            cell-level factor matrix. 
        num_epochs: int
            Number of training epochs.
        learning_rate: float
            Parameter for training.
        batch_size: int
            Size of batch processing.
        algo: str
            Optimization algorithm.
        beta_1: float
            Parameter for optimization.
        weight_decay: float
            Parameter for optimization.
        decay_rate: float
            Parameter for optimization.
        use_jax: bool
            If toggled on, Jax will be used for speeding up. CAUTION: This will raise errors because of unknown reasons when it is called in
            the Python script or Jupyter notebook. It is OK if it is used when runing DensityFlowMO3 in the shell command.
        show_progress: bool
            verbose on or off
        """
        
        print('#### RNA ####')
        xs_rna_list = [self.preprocess(a,'rna',threshold=threshold) for a in xs_paired_dict['rna']]
        if xs_rna_unpaired_list is not None:
            for xs_rna_single in xs_rna_unpaired_list:
                xs_rna_list.append(self.preprocess(xs_rna_single,'rna',threshold=threshold))
        xs_rna = np.vstack(xs_rna_list)
        
        self.rna_perturb_model.fit(xs=xs_rna, us=us, ts=ts, cs=cs, num_epochs=num_epochs,
                                   learning_rate=learning_rate, batch_size=batch_size,
                                   algo=algo, beta_1=beta_1, weight_decay=weight_decay,
                                   decay_rate=decay_rate,config_enum=config_enum,threshold=threshold,
                                   use_jax=use_jax, show_progress=show_progress)
        
        print('#### ATAC ####')
        xs_atac_list = [self.preprocess(a,'atac',threshold=threshold) for a in xs_paired_dict['atac']]
        if xs_atac_unpaired_list is not None:
            for xs_atac_single in xs_atac_unpaired_list:
                xs_atac_list.append(self.preprocess(xs_atac_single,'atac',threshold=threshold))
        xs_atac = np.vstack(xs_atac_list)
        
        self.atac_perturb_model.fit(xs=xs_atac, us=us, ts=ts, cs=cs, num_epochs=num_epochs,
                                   learning_rate=learning_rate, batch_size=batch_size,
                                   algo=algo, beta_1=beta_1, weight_decay=weight_decay,
                                   decay_rate=decay_rate,config_enum=config_enum,threshold=threshold,
                                   use_jax=use_jax, show_progress=show_progress)
        
        print('#### Cross-Omics ####')
        xs_rna = np.vstack([self.preprocess(a,'rna',threshold=threshold) for a in xs_paired_dict['rna']])
        xs_rna = convert_to_tensor(xs_rna, dtype=self.dtype, device='cpu')
        
        xs_atac = np.vstack([self.preprocess(a,'atac',threshold=threshold) for a in xs_paired_dict['atac']])
        xs_atac = convert_to_tensor(xs_atac, dtype=self.dtype, device='cpu')
        
        if us is not None:
            us = convert_to_tensor(us, dtype=self.dtype, device='cpu')
            ts = convert_to_tensor(ts, dtype=self.dtype, device='cpu')

        dataset = CustomDataset(xs_rna)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        # setup the optimizer
        optim_params = {'lr': learning_rate, 'betas': (beta_1, 0.999), 'weight_decay': weight_decay}

        if algo.lower()=='rmsprop':
            optimizer = torch.optim.RMSprop
        elif algo.lower()=='adam':
            optimizer = torch.optim.Adam
        elif algo.lower() == 'adamw':
            optimizer = torch.optim.AdamW
        else:
            raise ValueError("An optimization algorithm must be specified.")
        scheduler = ExponentialLR({'optimizer': optimizer, 'optim_args': optim_params, 'gamma': decay_rate})

        pyro.clear_param_store()

        # set up the loss(es) for inference, wrapping the guide in config_enumerate builds the loss as a sum
        # by enumerating each class label form the sampled discrete categorical distribution in the model
        Elbo = JitTraceEnum_ELBO if use_jax else TraceEnum_ELBO
        elbo = Elbo(max_plate_nesting=1, strict_enumeration_warning=False)
        
        cross_guide = config_enumerate(self.cross_guide, config_enum, expand=True)
        cross_loss = SVI(self.cross_model, cross_guide, scheduler, loss=elbo)
        
        # loss functions
        losses = [cross_loss]
        num_losses = len(losses)

        with tqdm(total=num_epochs, disable=not show_progress, desc='Training', unit='epoch') as pbar:
            for epoch in range(num_epochs):
                epoch_losses = [0.0] * num_losses
                for batch_x_rna, idx in dataloader:
                    batch_x_rna = batch_x_rna.to(self.get_device())
                    batch_x_atac = xs_atac[idx].to(self.get_device())
                    batch_u,batch_t = None,None
                    if us is not None:
                        batch_u = us[idx].to(self.get_device())
                        batch_t = ts[idx].to(self.get_device())
                    
                    # cross-omics
                    with torch.no_grad():
                        rna_ns_zs = self.rna_perturb_model._codebook_map(batch_x_rna, soft_assign=False).detach().clone()
                        rna_shifts = self.rna_perturb_model._cell_shift(rna_ns_zs, perturb=batch_u, perturb_type=batch_t)
                        
                        atac_ns_zs = self.atac_perturb_model._codebook_map(batch_x_atac, soft_assign=False).detach().clone()
                        atac_shifts = self.atac_perturb_model._cell_shift(atac_ns_zs, perturb=batch_u, perturb_type=batch_t)
                        
                    # cross-omics
                    loss_id = 0
                    new_loss = losses[loss_id].step(rna_ns_zs=rna_ns_zs, rna_shifts=rna_shifts, atac_ns_zs=atac_ns_zs, atac_shifts=atac_shifts)
                    epoch_losses[loss_id] += new_loss

                avg_epoch_losses_ = map(lambda v: v / len(dataloader), epoch_losses)
                avg_epoch_losses = map(lambda v: "{:.4f}".format(v), avg_epoch_losses_)

                # store the loss
                str_loss = " ".join(map(str, avg_epoch_losses))

                # Update progress bar
                pbar.set_postfix({'loss': str_loss})
                pbar.update(1)
                
    @classmethod
    def save_model(cls, model, file_path, compression=False):
        """Save the model to the specified file path."""
        file_path = os.path.abspath(file_path)

        model.eval()
        if compression:
            with gzip.open(file_path, 'wb') as pickle_file:
                pickle.dump(model, pickle_file)
        else:
            with open(file_path, 'wb') as pickle_file:
                pickle.dump(model, pickle_file)

        print(f'Model saved to {file_path}')

    @classmethod
    def load_model(cls, file_path):
        """Load the model from the specified file path and return an instance."""
        print(f'Model loaded from {file_path}')

        file_path = os.path.abspath(file_path)
        if file_path.endswith('gz'):
            with gzip.open(file_path, 'rb') as pickle_file:
                model = pickle.load(pickle_file)
        else:
            with open(file_path, 'rb') as pickle_file:
                model = pickle.load(pickle_file)
                
        return model
        
