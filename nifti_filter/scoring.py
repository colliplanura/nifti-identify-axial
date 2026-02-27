"""
Lógica de pontuação de séries NIfTI.

Funções para calcular score de classificação baseado em múltiplos
critérios (kernel, janela, descrição, tipo de imagem).
"""


def _as_text(value) -> str:
    """Converte valor para texto, tratando None e listas."""
    if value is None:
        return ""
    if isinstance(value, list):
        return "\\".join(str(v) for v in value)
    return str(value)


def _normalizar_lista_strings(value) -> list:
    """Normaliza valor para lista de strings lowercase."""
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip().lower() for v in value if str(v).strip()]
    texto = str(value).strip()
    if not texto:
        return []
    partes = [p.strip().lower() for p in texto.replace(",", "\\").split("\\")]
    return [p for p in partes if p]


# Padrões de kernel por fabricante (baseado em pesquisa pydicom, dcm2niix, OHIF)
KERNEL_PARTES_MOLES = [
    # Termos genéricos
    "soft", "stnd", "standard", "routine", "mediast", "smooth", "abd", "body",
    # Siemens
    "b10", "b20", "b30", "b31", "br", "i30s",
    # GE
    "fc01", "fc02", "fc03", "fc04", "fc05", "fc06", "fc07", "fc08", "fc09",
    "fc10", "fc11", "fc12", "fc13",
    # Philips
    "a", "b", "c",
]

KERNEL_PULMAO = [
    # Termos genéricos
    "lung", "pulm", "parench",
    # Siemens
    "b50", "b60", "b70", "i70f",
    # GE
    "fc50", "fc51", "fc52", "fc53", "fc54", "fc55", "fc56",
    # Philips
    "l", "la", "lb",
]

KERNEL_OSSO = [
    # Termos genéricos
    "bone", "sharp", "edge", "hr",
    # Siemens
    "b60", "b70", "b80", "i70h",
    # GE
    "fc80", "fc81", "fc82", "fc83", "fc84", "fc85", "fc86",
    # Philips
    "y", "ya", "yb",
]

TERMOS_DESCARTE = [
    "mip", "mpr", "sag", "cor", "3d", "vrt", "minip", "reformat",
    "scout", "localizer", "topograma", "dose", "surview",
]

IMAGE_TYPE_DESCARTE = [
    "derived", "secondary", "reformatted", "mpr", "mip", "minip", 
    "vrt", "3d", "reformat", "localizer", "scout", "dose_info",
]


def _classificar_janela(window_center, window_width) -> tuple:
    """
    Classifica tipo de janela baseado em WindowCenter/WindowWidth.
    
    Returns:
        (tipo, score) onde tipo é 'partes_moles', 'pulmao', 'osso' ou None
    """
    if window_center is None or window_width is None:
        return (None, 0)
    
    try:
        wc = float(window_center)
        ww = float(window_width)
    except (TypeError, ValueError):
        return (None, 0)
    
    # Pulmão: WC=-600 a -400, WW=1500-2000
    if -700 <= wc <= -300 and 1200 <= ww <= 2500:
        return ('pulmao', -5)
    
    # Osso: WC=300-500, WW=1500-3000
    if 200 <= wc <= 600 and 1200 <= ww <= 3500:
        return ('osso', -5)
    
    # Partes Moles: WC=40-60, WW=300-450
    if 20 <= wc <= 100 and 200 <= ww <= 600:
        return ('partes_moles', +3)
    
    return (None, 0)


def pontuar_serie(data: dict, nifti_info: dict = None) -> dict:
    """
    Calcula score de classificação para uma série.
    
    Args:
        data: Metadados JSON da série (dcm2niix)
        nifti_info: Info do header NIfTI (opcional, fallback para SliceThickness)
        
    Returns:
        Dict com score, motivos e metadados extraídos
    """
    desc = _as_text(data.get("SeriesDescription", "")).lower()
    protocolo = _as_text(data.get("ProtocolName", "")).lower()
    kernel = _as_text(data.get("ConvolutionKernel", "")).lower()
    image_type_tokens = _normalizar_lista_strings(data.get("ImageType", []))
    image_type = " ".join(image_type_tokens)
    
    # Espessura: primeiro tenta JSON, depois NIfTI header
    try:
        espessura = float(data.get("SliceThickness", 0) or 0)
    except (TypeError, ValueError):
        espessura = 0.0
    
    if espessura == 0 and nifti_info:
        espessura = nifti_info.get('espessura', 0.0)
    
    # Número de slices do NIfTI
    num_slices = nifti_info.get('num_slices', 0) if nifti_info else 0
    
    # WindowCenter/WindowWidth
    window_center = data.get("WindowCenter")
    window_width = data.get("WindowWidth")
    
    score = 0
    motivos = []
    
    # Pontuação por ImageType
    if "original" in image_type_tokens:
        score += 2
        motivos.append("image type original")
    if "primary" in image_type_tokens:
        score += 1
        motivos.append("image type primary")
    
    # Pontuação por kernel - partes moles
    if any(t in kernel for t in KERNEL_PARTES_MOLES):
        score += 3
        motivos.append("kernel partes moles")
    
    # Pontuação por descrição/protocolo compatível
    termos_positivos = ["soft", "abd", "body", "mediast", "routine", "standard"]
    if any(t in desc for t in termos_positivos) or any(t in protocolo for t in termos_positivos):
        score += 2
        motivos.append("descrição/protocolo compatível")
    
    # Pontuação por janela
    tipo_janela, score_janela = _classificar_janela(window_center, window_width)
    if tipo_janela:
        score += score_janela
        motivos.append(f"janela {tipo_janela}")
    
    # Penalização por kernel pulmão/osso
    if any(t in kernel for t in KERNEL_PULMAO):
        score -= 4
        motivos.append("kernel pulmão")
    if any(t in kernel for t in KERNEL_OSSO):
        score -= 4
        motivos.append("kernel osso")
    
    # Penalização por termos de descarte em descrição/protocolo
    if any(t in desc for t in TERMOS_DESCARTE) or any(t in protocolo for t in TERMOS_DESCARTE):
        score -= 3
        motivos.append("descrição/protocolo não principal")
    
    # Penalização por ImageType derivado
    if any(t in image_type for t in IMAGE_TYPE_DESCARTE):
        score -= 3
        motivos.append("image type derivado/secundário")
    
    # Penalização forte para localizer/scout
    if "localizer" in image_type or "scout" in image_type:
        score -= 10
        motivos.append("localizer/scout")
    
    # Pontuação por espessura
    if 2.0 <= espessura <= 5.0:
        score += 1
        motivos.append("espessura de rotina")
    elif 0 < espessura < 1.5:
        score -= 1
        motivos.append("espessura fina (recon)")
    
    return {
        "score": score,
        "descricao": desc,
        "protocolo": protocolo,
        "kernel": kernel,
        "image_type": image_type_tokens,
        "espessura": espessura,
        "num_slices": num_slices,
        "window_center": window_center,
        "window_width": window_width,
        "motivos": motivos,
    }
