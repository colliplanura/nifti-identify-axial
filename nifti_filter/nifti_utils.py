"""
Utilitários para leitura de headers NIfTI usando nibabel.

Funções para obter informações do header NIfTI sem carregar
a imagem completa em memória.
"""

import nibabel as nib


def get_num_slices(nifti_path: str) -> int:
    """
    Retorna número de slices axiais do arquivo NIfTI.
    
    Lê apenas o header, não carrega a imagem em memória.
    
    Args:
        nifti_path: Caminho para arquivo .nii.gz
        
    Returns:
        Número de slices (dimensão Z, índice 2 do shape)
    """
    img = nib.load(nifti_path)
    shape = img.header.get_data_shape()
    return shape[2] if len(shape) >= 3 else 0


def get_slice_thickness(nifti_path: str) -> float:
    """
    Retorna espessura do corte em mm do arquivo NIfTI.
    
    Lê apenas o header, não carrega a imagem em memória.
    
    Args:
        nifti_path: Caminho para arquivo .nii.gz
        
    Returns:
        Espessura do corte em mm (pixdim[3])
    """
    img = nib.load(nifti_path)
    pixdim = img.header['pixdim']
    return float(pixdim[3]) if len(pixdim) > 3 else 0.0


def get_nifti_info(nifti_path: str) -> dict:
    """
    Retorna informações básicas do arquivo NIfTI.
    
    Args:
        nifti_path: Caminho para arquivo .nii.gz
        
    Returns:
        Dict com 'num_slices' e 'espessura'
    """
    img = nib.load(nifti_path)
    shape = img.header.get_data_shape()
    pixdim = img.header['pixdim']
    
    return {
        'num_slices': shape[2] if len(shape) >= 3 else 0,
        'espessura': float(pixdim[3]) if len(pixdim) > 3 else 0.0,
    }
