"""Testes para o módulo de pontuação."""

import json
from pathlib import Path

import pytest

from nifti_filter.scoring import (
    _as_text,
    _normalizar_lista_strings,
    _classificar_janela,
    pontuar_serie,
)


# Fixtures
@pytest.fixture
def fixture_dir():
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def axial_soft_data(fixture_dir):
    with open(fixture_dir / "axial_soft.json") as f:
        return json.load(f)


@pytest.fixture
def lung_data(fixture_dir):
    with open(fixture_dir / "lung.json") as f:
        return json.load(f)


@pytest.fixture
def bone_data(fixture_dir):
    with open(fixture_dir / "bone.json") as f:
        return json.load(f)


@pytest.fixture
def mip_data(fixture_dir):
    with open(fixture_dir / "mip.json") as f:
        return json.load(f)


# Testes _as_text
class TestAsText:
    def test_none(self):
        assert _as_text(None) == ""

    def test_string(self):
        assert _as_text("text") == "text"

    def test_list(self):
        assert _as_text(["a", "b", "c"]) == "a\\b\\c"

    def test_number(self):
        assert _as_text(42) == "42"


# Testes _normalizar_lista_strings
class TestNormalizarListaStrings:
    def test_none(self):
        assert _normalizar_lista_strings(None) == []

    def test_lista(self):
        assert _normalizar_lista_strings(["ORIGINAL", "PRIMARY"]) == ["original", "primary"]

    def test_string_com_virgulas(self):
        result = _normalizar_lista_strings("a, b, c")
        assert "a" in result
        assert "b" in result
        assert "c" in result

    def test_string_vazia(self):
        assert _normalizar_lista_strings("") == []


# Testes _classificar_janela
class TestClassificarJanela:
    def test_partes_moles(self):
        tipo, score = _classificar_janela(40, 400)
        assert tipo == "partes_moles"
        assert score > 0

    def test_pulmao(self):
        tipo, score = _classificar_janela(-600, 1500)
        assert tipo == "pulmao"
        assert score < 0

    def test_osso(self):
        tipo, score = _classificar_janela(400, 2000)
        assert tipo == "osso"
        assert score < 0

    def test_none_values(self):
        tipo, score = _classificar_janela(None, None)
        assert tipo is None
        assert score == 0


# Testes pontuar_serie
class TestPontuarSerie:
    def test_axial_soft_score_positivo(self, axial_soft_data):
        result = pontuar_serie(axial_soft_data)
        assert result["score"] > 0
        assert "kernel partes moles" in result["motivos"]

    def test_lung_score_negativo(self, lung_data):
        result = pontuar_serie(lung_data)
        assert result["score"] < 0
        assert "janela pulmao" in result["motivos"]

    def test_bone_score_negativo(self, bone_data):
        result = pontuar_serie(bone_data)
        assert result["score"] < 0
        assert "kernel osso" in result["motivos"]

    def test_mip_score_negativo(self, mip_data):
        result = pontuar_serie(mip_data)
        # MIP tem kernel soft (+3), mas descrição "MIP" (-3) e ImageType derivado (-3) = ~-3
        assert result["score"] <= 0
        assert "descrição/protocolo não principal" in result["motivos"]

    def test_nifti_info_fallback(self):
        data = {"SeriesDescription": "test"}
        nifti_info = {"num_slices": 100, "espessura": 2.5}
        result = pontuar_serie(data, nifti_info)
        assert result["num_slices"] == 100
        assert result["espessura"] == 2.5
