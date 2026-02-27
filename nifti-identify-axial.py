import argparse
import json
import os
from glob import glob


def _as_text(value):
    if value is None:
        return ""
    if isinstance(value, list):
        return "\\".join(str(v) for v in value)
    return str(value)


def _normalizar_lista_strings(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip().lower() for v in value if str(v).strip()]
    texto = str(value).strip()
    if not texto:
        return []
    partes = [p.strip().lower() for p in texto.replace(",", "\\").split("\\")]
    return [p for p in partes if p]


def _is_axial_por_orientacao(orientacao, tolerancia=0.90):
    if not isinstance(orientacao, list) or len(orientacao) != 6:
        return False
    try:
        rx, ry, rz, cx, cy, cz = [float(v) for v in orientacao]
    except (TypeError, ValueError):
        return False

    nx = ry * cz - rz * cy
    ny = rz * cx - rx * cz
    nz = rx * cy - ry * cx

    return abs(nz) >= tolerancia


def _pontuar_serie_json(data):
    orientacao = data.get("ImageOrientationPatientDICOM", [])
    if not _is_axial_por_orientacao(orientacao):
        return None

    desc = _as_text(data.get("SeriesDescription", "")).lower()
    protocolo = _as_text(data.get("ProtocolName", "")).lower()
    kernel = _as_text(data.get("ConvolutionKernel", "")).lower()
    image_type_tokens = _normalizar_lista_strings(data.get("ImageType", []))
    image_type = " ".join(image_type_tokens)

    try:
        espessura = float(data.get("SliceThickness", 0) or 0)
    except (TypeError, ValueError):
        espessura = 0.0

    score = 0
    motivos = []

    score += 4
    motivos.append("axial por orientação")

    if "original" in image_type_tokens:
        score += 2
        motivos.append("image type original")
    if "primary" in image_type_tokens:
        score += 1
        motivos.append("image type primary")

    termos_positivos = [
        "soft", "stnd", "standard", "routine", "mediast", "smooth", "abd", "body", "br"
    ]
    termos_negativos = [
        "bone", "lung", "sharp", "edge", "hr", "mip", "mpr", "sag", "cor", "3d"
    ]

    if any(t in kernel for t in termos_positivos):
        score += 3
        motivos.append("kernel partes moles")
    if any(t in desc for t in termos_positivos) or any(t in protocolo for t in termos_positivos):
        score += 2
        motivos.append("descrição/protocolo compatível")

    if any(t in kernel for t in termos_negativos):
        score -= 4
        motivos.append("kernel não partes moles")
    if any(t in desc for t in termos_negativos) or any(t in protocolo for t in termos_negativos):
        score -= 3
        motivos.append("descrição/protocolo não principal")

    if any(t in image_type for t in ["derived", "secondary"]):
        score -= 3
        motivos.append("image type derivado/secundário")

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
        "motivos": motivos,
    }

def identificar_serie_local(debug=False):
    candidatos = []
    
    # Busca todos os JSONs no diretório atual
    arquivos_json = glob("*.json")
    
    if not arquivos_json:
        print("Nenhum arquivo .json encontrado no diretório corrente.")
        return None

    for caminho_json in arquivos_json:
        # Tenta abrir o JSON correspondente
        try:
            with open(caminho_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            continue

        avaliacao = _pontuar_serie_json(data)
        if not avaliacao:
            continue

        # Verifica se o arquivo .nii.gz correspondente realmente existe
        arquivo_nii = caminho_json.replace(".json", ".nii.gz")
        if os.path.exists(arquivo_nii):
            candidatos.append({
                "arquivo": arquivo_nii,
                "descricao": avaliacao["descricao"],
                "protocolo": avaliacao["protocolo"],
                "kernel": avaliacao["kernel"],
                "image_type": avaliacao["image_type"],
                "espessura": avaliacao["espessura"],
                "score": avaliacao["score"],
                "motivos": avaliacao["motivos"],
            })

    # Ordena pelo score (maior primeiro)
    candidatos.sort(key=lambda x: (x['score'], -abs((x['espessura'] or 0) - 3.5)), reverse=True)

    if debug and candidatos:
        print("\n[DEBUG] Ranking completo das séries candidatas:")
        for i, c in enumerate(candidatos, start=1):
            image_type_fmt = " | ".join(c["image_type"]) if c["image_type"] else "-"
            motivos_fmt = ", ".join(c["motivos"]) if c["motivos"] else "-"
            print(f" {i:02d}. {c['arquivo']}")
            print(f"     Score: {c['score']}")
            print(f"     Kernel: {c['kernel'] or '-'}")
            print(f"     Descrição: {c['descricao'] or '-'}")
            print(f"     Protocolo: {c['protocolo'] or '-'}")
            print(f"     ImageType: {image_type_fmt}")
            print(f"     Espessura: {c['espessura']}")
            print(f"     Motivos: {motivos_fmt}")

    return candidatos

# Execução
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Identifica a série axial principal de partes moles usando JSONs do dcm2niix."
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Exibe ranking completo e critérios de pontuação de todas as séries candidatas.",
    )
    args = parser.parse_args()

    resultados = identificar_serie_local(debug=args.debug)
    
    if resultados:
        melhor = resultados[0]
        print(f"✅ Série Principal Detectada: {melhor['arquivo']}")
        print(f"   Descrição: {melhor['descricao']}")
        print(f"   Protocolo: {melhor['protocolo']}")
        print(f"   Kernel: {melhor['kernel']}")
        print(f"   ImageType: {' | '.join(melhor['image_type']) if melhor['image_type'] else '-'}")
        print(f"   Espessura: {melhor['espessura']}")
        print(f"   Score: {melhor['score']}")
        print(f"   Motivos: {', '.join(melhor['motivos'])}")
        
        # Opcional: listar os outros para conferência
        if len(resultados) > 1:
            print("\nOutras séries encontradas (em ordem de relevância):")
            for r in resultados[1:]:
                print(f" - {r['arquivo']} (Score: {r['score']}, Kernel: {r['kernel']}, Esp.: {r['espessura']})")
    else:
        print("❌ Nenhuma série axial de partes moles identificada no diretório.")
