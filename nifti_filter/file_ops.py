"""
Operações de sistema de arquivos para o filtro NIfTI.

Funções para descoberta de séries e movimentação de arquivos.
"""

import json
import os
import shutil
from pathlib import Path
from typing import Iterator, Optional, Tuple


def descobrir_series(
    diretorio: str,
    recursivo: bool = False
) -> Iterator[Tuple[str, Optional[str]]]:
    """
    Descobre pares de arquivos NIfTI (.nii.gz) e JSON correspondentes.
    
    Args:
        diretorio: Caminho do diretório a ser escaneado
        recursivo: Se True, busca em subdiretórios
        
    Yields:
        Tuplas (caminho_nii, caminho_json) onde caminho_json pode ser None
    """
    diretorio_path = Path(diretorio)
    
    if not diretorio_path.is_dir():
        return
    
    if recursivo:
        nii_files = diretorio_path.rglob("*.nii.gz")
    else:
        nii_files = diretorio_path.glob("*.nii.gz")
    
    for nii_path in sorted(nii_files):
        # Pula arquivos no diretório de descarte
        if "descarte" in nii_path.parts:
            continue
        
        # Procura JSON correspondente (mesmo nome base)
        json_path = nii_path.with_suffix("").with_suffix(".json")
        if json_path.exists():
            yield (str(nii_path), str(json_path))
        else:
            yield (str(nii_path), None)


def carregar_json(caminho_json: str) -> dict:
    """
    Carrega metadados de arquivo JSON.
    
    Args:
        caminho_json: Caminho do arquivo JSON
        
    Returns:
        Dict com metadados ou dict vazio se falhar
    """
    if not caminho_json:
        return {}
    
    try:
        with open(caminho_json, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError, IOError):
        return {}


def mover_para_descarte(
    arquivo_nii: str,
    arquivo_json: Optional[str],
    diretorio_descarte: str = "descarte",
    dry_run: bool = False,
) -> Tuple[bool, str]:
    """
    Move arquivos para o diretório de descarte.
    
    Args:
        arquivo_nii: Caminho do arquivo .nii.gz
        arquivo_json: Caminho do arquivo .json (pode ser None)
        diretorio_descarte: Nome do diretório de descarte
        dry_run: Se True, não move arquivos (apenas simula)
        
    Returns:
        Tupla (sucesso, mensagem)
    """
    nii_path = Path(arquivo_nii)
    diretorio_origem = nii_path.parent
    destino_base = diretorio_origem / diretorio_descarte
    
    destino_nii = destino_base / nii_path.name
    
    if dry_run:
        msg = f"[DRY-RUN] Moveria {nii_path.name} → {destino_base}/"
        return (True, msg)
    
    try:
        # Cria diretório de descarte se não existir
        destino_base.mkdir(parents=True, exist_ok=True)
        
        # Move arquivo NIfTI (sobrescreve se existir)
        if destino_nii.exists():
            destino_nii.unlink()
        shutil.move(str(nii_path), str(destino_nii))
        
        # Move arquivo JSON correspondente se existir
        if arquivo_json:
            json_path = Path(arquivo_json)
            if json_path.exists():
                destino_json = destino_base / json_path.name
                if destino_json.exists():
                    destino_json.unlink()
                shutil.move(str(json_path), str(destino_json))
        
        return (True, f"Movido: {nii_path.name} → {diretorio_descarte}/")
    
    except OSError as e:
        return (False, f"Erro ao mover {nii_path.name}: {e}")


def contar_arquivos(diretorio: str, recursivo: bool = False) -> dict:
    """
    Conta arquivos NIfTI e JSON no diretório.
    
    Args:
        diretorio: Caminho do diretório
        recursivo: Se True, conta em subdiretórios
        
    Returns:
        Dict com contagem de arquivos por tipo
    """
    diretorio_path = Path(diretorio)
    
    if recursivo:
        nii_count = len(list(diretorio_path.rglob("*.nii.gz")))
        json_count = len(list(diretorio_path.rglob("*.json")))
    else:
        nii_count = len(list(diretorio_path.glob("*.nii.gz")))
        json_count = len(list(diretorio_path.glob("*.json")))
    
    return {
        "nii": nii_count,
        "json": json_count,
    }
