"""Testes para o módulo de classificação."""

import json
from pathlib import Path

import pytest

from nifti_filter.classifier import (
    AvaliacaoSerie,
    is_axial_por_orientacao,
    classificar_serie,
)
from nifti_filter.scoring import pontuar_serie


# Fixtures
@pytest.fixture
def fixture_dir():
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def axial_soft_data(fixture_dir):
    with open(fixture_dir / "axial_soft.json") as f:
        return json.load(f)


@pytest.fixture
def coronal_data(fixture_dir):
    with open(fixture_dir / "coronal.json") as f:
        return json.load(f)


# Testes is_axial_por_orientacao
class TestIsAxialPorOrientacao:
    def test_axial(self):
        # Orientação axial padrão: row=[1,0,0], col=[0,1,0]
        orient = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0]
        assert is_axial_por_orientacao(orient) is True

    def test_coronal(self):
        # Orientação coronal: row=[1,0,0], col=[0,0,-1]
        orient = [1.0, 0.0, 0.0, 0.0, 0.0, -1.0]
        assert is_axial_por_orientacao(orient) is False

    def test_sagital(self):
        # Orientação sagital: row=[0,1,0], col=[0,0,-1]
        orient = [0.0, 1.0, 0.0, 0.0, 0.0, -1.0]
        assert is_axial_por_orientacao(orient) is False

    def test_lista_vazia(self):
        assert is_axial_por_orientacao([]) is False

    def test_lista_invalida(self):
        assert is_axial_por_orientacao([1, 2, 3]) is False

    def test_none(self):
        assert is_axial_por_orientacao(None) is False

    def test_tolerancia_custom(self):
        # Orientação levemente inclinada
        orient = [0.9, 0.1, 0.0, 0.0, 0.9, 0.1]
        assert is_axial_por_orientacao(orient, tolerancia=0.7) is True
        assert is_axial_por_orientacao(orient, tolerancia=0.95) is False


# Testes classificar_serie
class TestClassificarSerie:
    def test_axial_soft_nao_descarta(self, axial_soft_data):
        score_result = pontuar_serie(axial_soft_data, {"num_slices": 50, "espessura": 2.0})
        result = classificar_serie(
            arquivo_nii="/test/axial.nii.gz",
            arquivo_json="/test/axial.json",
            data=axial_soft_data,
            avaliacao_score=score_result,
            threshold=0,
            espessura_min=0.5,
            espessura_max=3.0,
            min_slices=30,
        )
        assert isinstance(result, AvaliacaoSerie)
        assert result.is_axial is True
        assert result.descarte is False

    def test_coronal_descarta(self, coronal_data):
        score_result = pontuar_serie(coronal_data, {"num_slices": 50, "espessura": 2.0})
        result = classificar_serie(
            arquivo_nii="/test/coronal.nii.gz",
            arquivo_json="/test/coronal.json",
            data=coronal_data,
            avaliacao_score=score_result,
            threshold=0,
        )
        assert result.is_axial is False
        assert result.descarte is True

    def test_espessura_fora_limite_descarta(self, axial_soft_data):
        axial_soft_data["SliceThickness"] = 5.0  # Fora do limite
        score_result = pontuar_serie(axial_soft_data, {"num_slices": 50, "espessura": 5.0})
        result = classificar_serie(
            arquivo_nii="/test/thick.nii.gz",
            arquivo_json="/test/thick.json",
            data=axial_soft_data,
            avaliacao_score=score_result,
            espessura_max=3.0,
        )
        assert result.espessura_valida is False
        assert result.descarte is True

    def test_poucas_imagens_descarta(self, axial_soft_data):
        score_result = pontuar_serie(axial_soft_data, {"num_slices": 10, "espessura": 2.0})
        result = classificar_serie(
            arquivo_nii="/test/few.nii.gz",
            arquivo_json="/test/few.json",
            data=axial_soft_data,
            avaliacao_score=score_result,
            min_slices=30,
        )
        assert result.num_slices_valido is False
        assert result.descarte is True

    def test_threshold_customizado(self, axial_soft_data):
        score_result = pontuar_serie(axial_soft_data, {"num_slices": 50, "espessura": 2.0})
        # Com threshold alto, série com score médio será descartada
        result = classificar_serie(
            arquivo_nii="/test/test.nii.gz",
            arquivo_json="/test/test.json",
            data=axial_soft_data,
            avaliacao_score=score_result,
            threshold=100,  # Threshold muito alto
        )
        assert result.descarte is True
