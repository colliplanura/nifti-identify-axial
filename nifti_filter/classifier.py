"""
Classificação de séries NIfTI.

Funções para classificar séries por orientação e decidir descarte.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class AvaliacaoSerie:
    """Resultado da avaliação de uma série."""
    arquivo_nii: str
    arquivo_json: Optional[str]
    score: int
    motivos: List[str]
    is_axial: bool
    espessura: float
    num_slices: int
    espessura_valida: bool
    num_slices_valido: bool
    descarte: bool
    # Metadados para debug
    kernel: str = ""
    descricao: str = ""
    protocolo: str = ""
    image_type: List[str] = None
    
    def __post_init__(self):
        if self.image_type is None:
            self.image_type = []


def is_axial_por_orientacao(orientacao: list, tolerancia: float = 0.90) -> bool:
    """
    Verifica se orientação é axial baseado em ImageOrientationPatientDICOM.
    
    Calcula o vetor normal ao plano de imagem e verifica se o componente Z
    é dominante (maior ou igual à tolerância).
    
    Args:
        orientacao: Lista com 6 valores de cossenos diretores [rx, ry, rz, cx, cy, cz]
        tolerancia: Valor mínimo para componente Z ser considerado dominante
        
    Returns:
        True se a orientação é axial
    """
    if not isinstance(orientacao, list) or len(orientacao) != 6:
        return False
    
    try:
        rx, ry, rz, cx, cy, cz = [float(v) for v in orientacao]
    except (TypeError, ValueError):
        return False
    
    # Vetor normal ao plano de imagem (produto vetorial)
    nx = ry * cz - rz * cy
    ny = rz * cx - rx * cz
    nz = rx * cy - ry * cx
    
    # É axial se componente Z é dominante
    return abs(nz) >= tolerancia


def classificar_serie(
    arquivo_nii: str,
    arquivo_json: Optional[str],
    data: dict,
    avaliacao_score: dict,
    threshold: int = 0,
    espessura_min: float = 0.5,
    espessura_max: float = 3.0,
    min_slices: int = 30,
    tolerancia_axial: float = 0.90,
) -> AvaliacaoSerie:
    """
    Classifica uma série e decide se deve ser descartada.
    
    Args:
        arquivo_nii: Caminho do arquivo .nii.gz
        arquivo_json: Caminho do arquivo .json (pode ser None)
        data: Metadados JSON da série
        avaliacao_score: Resultado de pontuar_serie()
        threshold: Score mínimo para manter série
        espessura_min: Espessura mínima válida em mm
        espessura_max: Espessura máxima válida em mm
        min_slices: Quantidade mínima de imagens
        tolerancia_axial: Tolerância para classificar como axial
        
    Returns:
        AvaliacaoSerie com decisão de descarte
    """
    orientacao = data.get("ImageOrientationPatientDICOM", [])
    is_axial = is_axial_por_orientacao(orientacao, tolerancia_axial)
    
    score = avaliacao_score.get("score", 0)
    espessura = avaliacao_score.get("espessura", 0.0)
    num_slices = avaliacao_score.get("num_slices", 0)
    motivos = list(avaliacao_score.get("motivos", []))
    
    # Adicionar pontuação de orientação
    if is_axial:
        score += 4
        motivos.insert(0, "axial por orientação")
    else:
        motivos.insert(0, "orientação não-axial")
    
    # Validações
    espessura_valida = espessura_min <= espessura <= espessura_max if espessura > 0 else False
    num_slices_valido = num_slices >= min_slices if num_slices > 0 else True  # Se não souber, não penaliza
    
    # Decisão de descarte
    descarte = (
        score <= threshold or
        not is_axial or
        (espessura > 0 and not espessura_valida) or
        (num_slices > 0 and not num_slices_valido)
    )
    
    # Adicionar motivos de descarte
    if not espessura_valida and espessura > 0:
        if espessura < espessura_min:
            motivos.append(f"espessura muito fina ({espessura:.1f}mm)")
        elif espessura > espessura_max:
            motivos.append(f"espessura muito grossa ({espessura:.1f}mm)")
    
    if not num_slices_valido and num_slices > 0:
        motivos.append(f"poucas imagens ({num_slices})")
    
    return AvaliacaoSerie(
        arquivo_nii=arquivo_nii,
        arquivo_json=arquivo_json,
        score=score,
        motivos=motivos,
        is_axial=is_axial,
        espessura=espessura,
        num_slices=num_slices,
        espessura_valida=espessura_valida,
        num_slices_valido=num_slices_valido,
        descarte=descarte,
        kernel=avaliacao_score.get("kernel", ""),
        descricao=avaliacao_score.get("descricao", ""),
        protocolo=avaliacao_score.get("protocolo", ""),
        image_type=avaliacao_score.get("image_type", []),
    )
