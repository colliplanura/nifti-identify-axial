"""
NIfTI Filter - Filtro de Séries NIfTI Axiais de Partes Moles

CLI para filtrar séries NIfTI axiais de partes moles com cortes finos,
movendo séries não relevantes para diretório de descarte.

Desenvolvido no âmbito do Doutorado em Ciências Médicas pelo
Instituto D'Or de Pesquisa e Ensino (IDOR), sob orientação dos Doutores
Alysson Roncally Silva Carvalho, Rodrigo Basilio e Rosana Souza Rodrigues.
"""

__version__ = "0.1.0"
__author__ = "Sandro Colli"
__email__ = "colliplanura@gmail.com"
__institution__ = "Instituto D'Or de Pesquisa e Ensino (IDOR)"
__citation__ = "Colli, Sandro"

from .classifier import AvaliacaoSerie, classificar_serie, is_axial_por_orientacao
from .file_ops import carregar_json, descobrir_series, mover_para_descarte
from .nifti_utils import get_nifti_info, get_num_slices, get_slice_thickness
from .scoring import pontuar_serie

__all__ = [
    "__version__",
    # classifier
    "AvaliacaoSerie",
    "classificar_serie",
    "is_axial_por_orientacao",
    # file_ops
    "carregar_json",
    "descobrir_series",
    "mover_para_descarte",
    # nifti_utils
    "get_nifti_info",
    "get_num_slices",
    "get_slice_thickness",
    # scoring
    "pontuar_serie",
]
