"""
CLI para filtro de séries NIfTI axiais de partes moles.

Processa diretório com arquivos NIfTI e move séries não relevantes
para um subdiretório de descarte.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from . import __version__
from .classifier import AvaliacaoSerie, classificar_serie
from .file_ops import carregar_json, descobrir_series, mover_para_descarte
from .nifti_utils import get_nifti_info
from .scoring import pontuar_serie


def criar_parser() -> argparse.ArgumentParser:
    """Cria parser de argumentos conforme contracts/cli-args.md."""
    parser = argparse.ArgumentParser(
        prog="nifti-filter",
        description="Filtra séries NIfTI axiais de partes moles com cortes finos.",
        epilog="Séries não relevantes são movidas para descarte/",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "diretorio",
        nargs="?",
        default=".",
        help="Diretório contendo arquivos .nii.gz e .json (default: diretório atual)",
    )
    
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Processar subdiretórios recursivamente",
    )
    
    parser.add_argument(
        "-n", "--dry-run",
        action="store_true",
        help="Apenas listar arquivos, não mover",
    )
    
    parser.add_argument(
        "-d", "--debug",
        action="store_true",
        help="Exibir ranking detalhado de todas as séries",
    )
    
    parser.add_argument(
        "-t", "--threshold",
        type=int,
        default=0,
        help="Score mínimo para manter série (default: 0)",
    )
    
    parser.add_argument(
        "--espessura-min",
        type=float,
        default=0.5,
        help="Espessura mínima de corte em mm (default: 0.5)",
    )
    
    parser.add_argument(
        "--espessura-max",
        type=float,
        default=3.0,
        help="Espessura máxima de corte em mm (default: 3.0)",
    )
    
    parser.add_argument(
        "--min-slices",
        type=int,
        default=30,
        help="Quantidade mínima de imagens na série (default: 30)",
    )
    
    parser.add_argument(
        "--tolerancia-axial",
        type=float,
        default=0.90,
        help="Tolerância para classificar orientação como axial (default: 0.90)",
    )
    
    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    
    return parser


def exibir_ranking_debug(avaliacoes: List[AvaliacaoSerie]) -> None:
    """Exibe ranking detalhado de todas as séries (modo --debug)."""
    # Ordenar por score decrescente
    avaliacoes_sorted = sorted(avaliacoes, key=lambda a: a.score, reverse=True)
    
    print("\n" + "=" * 80)
    print("RANKING DE SÉRIES (--debug)")
    print("=" * 80)
    
    for i, av in enumerate(avaliacoes_sorted, 1):
        nome = Path(av.arquivo_nii).name
        status = "MANTER" if not av.descarte else "DESCARTAR"
        
        print(f"\n{i}. [{status}] {nome}")
        print(f"   Score: {av.score:+d}")
        print(f"   Axial: {'Sim' if av.is_axial else 'Não'}")
        print(f"   Espessura: {av.espessura:.2f}mm ({'OK' if av.espessura_valida else 'Fora do limite'})")
        print(f"   Slices: {av.num_slices} ({'OK' if av.num_slices_valido else 'Abaixo do mínimo'})")
        print(f"   Kernel: {av.kernel or '(não informado)'}")
        print(f"   Descrição: {av.descricao or '(não informada)'}")
        print(f"   ImageType: {', '.join(av.image_type) if av.image_type else '(não informado)'}")
        print(f"   Motivos: {', '.join(av.motivos)}")
    
    print("\n" + "=" * 80)


def processar_diretorio(args: argparse.Namespace) -> int:
    """
    Processa diretório e move séries não relevantes para descarte.
    
    Args:
        args: Argumentos do CLI
        
    Returns:
        Código de saída (0 = sucesso)
    """
    diretorio = Path(args.diretorio)
    
    if not diretorio.is_dir():
        print(f"Erro: diretório não encontrado: {diretorio}", file=sys.stderr)
        return 1
    
    print(f"Processando: {diretorio.absolute()}")
    if args.recursive:
        print("Modo: recursivo")
    if args.dry_run:
        print("Modo: dry-run (nenhum arquivo será movido)")
    
    # Coletar avaliações
    avaliacoes: List[AvaliacaoSerie] = []
    
    for arquivo_nii, arquivo_json in descobrir_series(str(diretorio), args.recursive):
        # Carregar metadados JSON
        data = carregar_json(arquivo_json) if arquivo_json else {}
        
        # Obter info do header NIfTI (fallback para SliceThickness)
        try:
            nifti_info = get_nifti_info(arquivo_nii)
        except Exception as e:
            if args.debug:
                print(f"Aviso: Não foi possível ler header de {arquivo_nii}: {e}", file=sys.stderr)
            nifti_info = {}
        
        # Pontuar série
        score_result = pontuar_serie(data, nifti_info)
        
        # Classificar série
        avaliacao = classificar_serie(
            arquivo_nii=arquivo_nii,
            arquivo_json=arquivo_json,
            data=data,
            avaliacao_score=score_result,
            threshold=args.threshold,
            espessura_min=args.espessura_min,
            espessura_max=args.espessura_max,
            min_slices=args.min_slices,
            tolerancia_axial=args.tolerancia_axial,
        )
        
        avaliacoes.append(avaliacao)
    
    # Exibir ranking debug se solicitado
    if args.debug:
        exibir_ranking_debug(avaliacoes)
    
    # Movimentar arquivos
    mantidas = [a for a in avaliacoes if not a.descarte]
    descartadas = [a for a in avaliacoes if a.descarte]
    
    for av in descartadas:
        sucesso, msg = mover_para_descarte(
            av.arquivo_nii,
            av.arquivo_json,
            dry_run=args.dry_run,
        )
        if args.debug or args.dry_run:
            print(msg)
        elif not sucesso:
            print(msg, file=sys.stderr)
    
    # Resumo final
    print("\n" + "-" * 40)
    print("RESUMO")
    print("-" * 40)
    print(f"Total de séries: {len(avaliacoes)}")
    print(f"Mantidas: {len(mantidas)}")
    print(f"Descartadas: {len(descartadas)}")
    
    if mantidas and not args.debug:
        print("\nSéries mantidas:")
        for av in sorted(mantidas, key=lambda a: a.score, reverse=True):
            nome = Path(av.arquivo_nii).name
            print(f"  [{av.score:+d}] {nome}")
    
    if args.dry_run:
        print("\n[DRY-RUN] Nenhum arquivo foi movido.")
    
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    """
    Ponto de entrada principal do CLI.
    
    Args:
        argv: Argumentos de linha de comando (usa sys.argv se None)
        
    Returns:
        Código de saída (0 = sucesso)
    """
    parser = criar_parser()
    args = parser.parse_args(argv)
    
    try:
        return processar_diretorio(args)
    except KeyboardInterrupt:
        print("\nOperação cancelada pelo usuário.", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Erro: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
