# Metodologias para Classificação de Séries CT por Tipo de Janela/Kernel

## Sumário Executivo

Este documento consolida metodologias verificadas para identificar e classificar séries de tomografia computadorizada (CT) por:
1. Tipo de janela (Lung, Bone, Soft Tissue)
2. Tipo de kernel de reconstrução
3. Diferenciação entre aquisições originais e reconstruções derivadas (MIP, MPR, 3D)

---

## 1. Campos DICOM Relevantes

### 1.1 Campos Primários para Classificação

| Tag DICOM | Nome | Descrição | Uso na Classificação |
|-----------|------|-----------|---------------------|
| (0018,1210) | **ConvolutionKernel** | Nome do kernel/filtro de reconstrução | Identifica tipo de tecido/resolução |
| (0028,1050) | **WindowCenter** | Centro do nível de janela | Identifica tipo de visualização |
| (0028,1051) | **WindowWidth** | Largura da janela | Complementa WindowCenter |
| (0008,0008) | **ImageType** | Tipo de imagem (ORIGINAL/DERIVED) | Distingue aquisições vs reconstruções |
| (0008,103E) | **SeriesDescription** | Descrição da série | Texto livre com keywords |
| (0018,5100) | **PatientPosition** | Posição do paciente | Validação de orientação |
| (0020,0037) | **ImageOrientationPatient** | Orientação da imagem | Determina plano (axial/coronal/sagital) |

### 1.2 Campos Secundários

| Tag DICOM | Nome | Uso |
|-----------|------|-----|
| (0008,0060) | Modality | Deve ser "CT" |
| (0018,0050) | SliceThickness | Distingue alta resolução vs standard |
| (0018,0088) | SpacingBetweenSlices | Reconstruções volumétricas |
| (0028,0004) | PhotometricInterpretation | Deve ser MONOCHROME1 ou MONOCHROME2 |
| (0028,1055) | WindowCenterWidthExplanation | Label associado à janela |
| (0018,1160) | FilterType | Tipo de filtro adicional |
| (0018,9315) | ReconstructionAlgorithm | Algoritmo específico |

---

## 2. Padrões de Kernel por Fabricante

### 2.1 Siemens

| Kernel | Tipo | Descrição |
|--------|------|-----------|
| **B10f, B20f** | Soft Tissue | Kernels suaves para partes moles |
| **B30f, B31f** | Standard | Balanço entre resolução e ruído |
| **B40f, B41f** | Standard/Lung | Uso geral torácico |
| **B50f** | Lung | Kernel de pulmão padrão |
| **B60f, B70f** | Sharp/Bone | Alta resolução espacial |
| **B70h, B75h** | Bone/HR | Kernels muito duros para osso |
| **B80f, B80h** | Ultra-Sharp | Máxima resolução (pulmão HRCT) |
| **Br36f, Br40f** | Brain | Kernels cerebrais dedicados |
| **H10s, H20s, H30s** | Soft SAFIRE | Reconstrução iterativa suave |
| **I70f, I80f** | Iterative Sharp | Reconstrução iterativa aguda |

**Padrão de nomenclatura Siemens:**
- Letra inicial: B=Body, Br=Brain, H=Head, I=Iterative
- Número: quanto maior, mais sharp/resolução
- Sufixo: f=filtered, h=high-resolution, s=SAFIRE

### 2.2 GE Healthcare

| Kernel | Tipo | Descrição |
|--------|------|-----------|
| **STANDARD** | Standard | Kernel padrão partes moles |
| **SOFT** | Soft Tissue | Suavização máxima |
| **DETAIL** | Detail | Balanço resolução/ruído |
| **LUNG** | Lung | Otimizado para parênquima pulmonar |
| **BONE** | Bone | Alta resolução para osso |
| **BONEPLUS** | Bone | Maior resolução óssea |
| **EDGE** | Sharp | Máxima nitidez |
| **CHEST** | Chest | Combinação para tórax |
| **FC01-FC05** | Soft | Kernels suaves numerados |
| **FC10-FC17** | Standard | Kernels médios |
| **FC30, FC50** | Sharp | Kernels agudos |
| **FC51-FC56** | Bone | Kernels ósseos |
| **FC80-FC86** | Lung | Kernels pulmonares |

### 2.3 Philips

| Kernel | Tipo | Descrição |
|--------|------|-----------|
| **A** | Soft Tissue | Kernel suave (smooth) |
| **B** | Standard | Kernel padrão |
| **C** | Medium Sharp | Intermediário |
| **D** | Sharp | Resolução aumentada |
| **E** | Very Sharp | Alta resolução |
| **L** | Lung | Kernel pulmonar |
| **Y** | Bone | Kernel ósseo |
| **YA, YB** | Bone variants | Variantes ósseas |
| **UB, UC, UD** | Ultra | Família ultra resolução |
| **SOFT** | Soft Tissue | Label direto |
| **STANDARD** | Standard | Label direto |
| **LUNG** | Lung | Label direto |
| **BONE** | Bone | Label direto |

### 2.4 Canon/Toshiba

| Kernel | Tipo | Descrição |
|--------|------|-----------|
| **FC01** | Soft/Standard | Kernel suave |
| **FC02, FC03** | Standard | Kernels padrão |
| **FC04, FC05** | Soft | Partes moles |
| **FC10, FC11** | Standard | Corpo padrão |
| **FC12, FC13** | Medium | Intermediário |
| **FC30** | Sharp/Lung | Kernel agudo |
| **FC50, FC51** | Sharp/Bone | Kernel ósseo |
| **FC52** | Bone Plus | Alta resolução óssea |
| **FC80, FC81** | Lung | Kernel pulmonar |
| **FC83, FC85** | Lung Plus | Ultra resolução pulmão |

---

## 3. Ranges de WindowCenter/WindowWidth

### 3.1 Janelas Padrão Clínicas

| Tipo de Janela | WindowCenter (HU) | WindowWidth (HU) | Uso Clínico |
|----------------|-------------------|------------------|-------------|
| **Lung** | -600 a -400 | 1500 - 2000 | Parênquima pulmonar, enfisema |
| **Mediastinum** | 40 - 50 | 350 - 500 | Estruturas mediastinais |
| **Soft Tissue** | 40 - 60 | 300 - 400 | Tecidos moles gerais |
| **Bone** | 300 - 500 | 1500 - 3000 | Estruturas ósseas |
| **Brain** | 35 - 45 | 70 - 100 | Parênquima cerebral |
| **Stroke** | 30 - 40 | 30 - 40 | Detecção AVC agudo |
| **Subdural** | 75 - 100 | 200 - 300 | Hematoma subdural |
| **Liver** | 50 - 70 | 130 - 180 | Parênquima hepático |
| **Abdomen** | 40 - 50 | 350 - 400 | Abdômen geral |
| **Spine** | 300 - 400 | 1800 - 2500 | Coluna vertebral |

### 3.2 Valores Típicos Encontrados em Implementações (OHIF Viewer)

```
CT-Lung:       WC = -600, WW = 1500
CT-Soft-Tissue: WC = 40, WW = 400
CT-Bone:       WC = 400, WW = 2000 (ou WC = 300, WW = 1500)
CT-Mediastinum: WC = 50, WW = 450
```

### 3.3 Algoritmo de Classificação por Janela

```python
def classify_window(window_center, window_width):
    """
    Classifica o tipo de janela baseado em WC/WW.
    Retorna: 'LUNG', 'BONE', 'SOFT_TISSUE', 'BRAIN', 'UNKNOWN'
    """
    # Normalizar para float
    wc = float(window_center)
    ww = float(window_width)
    
    # Lung: centro negativo, largura ampla
    if -800 <= wc <= -300 and 1000 <= ww <= 2500:
        return 'LUNG'
    
    # Bone: centro alto positivo, largura ampla
    if 200 <= wc <= 600 and 1000 <= ww <= 4000:
        return 'BONE'
    
    # Brain: centro ~40, largura estreita
    if 20 <= wc <= 60 and 50 <= ww <= 120:
        return 'BRAIN'
    
    # Soft Tissue: centro baixo positivo, largura moderada
    if 20 <= wc <= 100 and 200 <= ww <= 500:
        return 'SOFT_TISSUE'
    
    return 'UNKNOWN'
```

---

## 4. Critérios de Classificação por ImageType

### 4.1 Estrutura do ImageType (0008,0008)

O campo ImageType é uma string com múltiplos valores separados por `\`:

```
Value 1: ORIGINAL ou DERIVED
Value 2: PRIMARY, SECONDARY, etc.
Value 3: Contexto específico (AXIAL, LOCALIZER, etc.)
Value 4+: Flags adicionais específicas do fabricante
```

### 4.2 Tokens para Identificar Aquisições Originais

| Token | Posição | Significado |
|-------|---------|-------------|
| **ORIGINAL** | 1 | Dados primários adquiridos |
| **PRIMARY** | 2 | Primeira reconstrução dos dados raw |
| **AXIAL** | 3+ | Plano axial original |
| **VOLUME** | 3+ | Dados volumétricos |
| **HELICOIDAL** | 3+ | Aquisição helicoidal |

**Exemplo de série original:**
```
ORIGINAL\PRIMARY\AXIAL
```

### 4.3 Tokens para Identificar Reconstruções Derivadas

| Token | Posição | Significado |
|-------|---------|-------------|
| **DERIVED** | 1 | Imagem derivada/processada |
| **SECONDARY** | 2 | Processamento secundário |
| **MPR** | 3+ | Multiplanar Reformatted |
| **MIP** | 3+ | Maximum Intensity Projection |
| **MINIP** | 3+ | Minimum Intensity Projection |
| **AVERAGE** | 3+ | Average Intensity Projection |
| **3D** | 3+ | Renderização 3D |
| **VRT** | 3+ | Volume Rendering Technique |
| **REFORMAT** | 3+ | Reformatação genérica |
| **CURVED** | 3+ | Reformatação curvilínea |
| **CPR** | 3+ | Curved Planar Reformation |
| **SLAB** | 3+ | Slab MIP/reconstrução |
| **LOCALIZER** | 3+ | Scout/Topogram |

**Exemplos de séries derivadas:**
```
DERIVED\PRIMARY\MPR
DERIVED\SECONDARY\MIP
ORIGINAL\PRIMARY\AXIAL\MIP    # Pode ocorrer
```

### 4.4 Algoritmo de Detecção de Reconstruções

```python
def is_derived_reconstruction(image_type, series_description=""):
    """
    Detecta se uma série é uma reconstrução derivada.
    
    Args:
        image_type: String do campo ImageType (0008,0008)
        series_description: String do campo SeriesDescription (0008,103E)
    
    Returns:
        tuple: (is_derived: bool, reconstruction_type: str)
    """
    if not image_type:
        return False, "UNKNOWN"
    
    # Normalizar para maiúsculas
    image_type_upper = image_type.upper()
    
    # Tokens de reconstrução derivada
    derived_tokens = [
        'DERIVED', 'MPR', 'MIP', 'MINIP', '3D', 'VRT', 
        'REFORMAT', 'CURVED', 'CPR', 'SLAB', 'AVERAGE',
        'VOLUME RENDERING', 'PROJECTION'
    ]
    
    # Verificar tokens no ImageType
    for token in derived_tokens:
        if token in image_type_upper:
            return True, token
    
    # Verificar SeriesDescription como fallback
    if series_description:
        desc_upper = series_description.upper()
        desc_patterns = {
            'MIP': ['MIP', 'MAXIP', 'MAX IP', 'MAXIMUM INTENSITY'],
            'MPR': ['MPR', 'MULTIPLANAR', 'REFORMAT'],
            '3D': ['3D', 'THREE-D', 'VOLUME RENDER', 'VRT'],
            'CORONAL': ['COR ', 'CORONAL'],
            'SAGITTAL': ['SAG ', 'SAGITTAL'],
            'OBLIQUE': ['OBLIQUE', 'OBL '],
        }
        
        for recon_type, patterns in desc_patterns.items():
            for pattern in patterns:
                if pattern in desc_upper:
                    return True, recon_type
    
    # Se começa com ORIGINAL e não tem tokens derivados
    if image_type_upper.startswith('ORIGINAL'):
        return False, "ORIGINAL"
    
    return False, "UNKNOWN"
```

---

## 5. Classificação Completa de Kernel por Tipo de Tecido

### 5.1 Algoritmo de Classificação por Kernel

```python
def classify_kernel(kernel_name, manufacturer=""):
    """
    Classifica o tipo de tecido baseado no nome do kernel.
    
    Returns: 'LUNG', 'BONE', 'SOFT_TISSUE', 'BRAIN', 'STANDARD', 'UNKNOWN'
    """
    if not kernel_name:
        return 'UNKNOWN'
    
    kernel_upper = kernel_name.upper().strip()
    
    # Padrões diretos (todos os fabricantes)
    if any(p in kernel_upper for p in ['LUNG', 'PULMO']):
        return 'LUNG'
    if any(p in kernel_upper for p in ['BONE', 'OSTEO']):
        return 'BONE'
    if any(p in kernel_upper for p in ['SOFT', 'HEAD', 'BRAIN']):
        return 'SOFT_TISSUE'
    
    # Siemens patterns
    siemens_patterns = {
        'LUNG': ['B50', 'B60', 'B70', 'B80', 'I70', 'I80'],
        'BONE': ['B70H', 'B75H', 'B80H'],
        'SOFT_TISSUE': ['B10', 'B20', 'B30', 'H10', 'H20', 'H30', 'BR'],
        'STANDARD': ['B31', 'B40', 'B41']
    }
    
    for tissue_type, patterns in siemens_patterns.items():
        for pattern in patterns:
            if kernel_upper.startswith(pattern):
                return tissue_type
    
    # GE patterns
    ge_patterns = {
        'LUNG': ['FC80', 'FC81', 'FC82', 'FC83', 'FC84', 'FC85', 'FC86'],
        'BONE': ['FC50', 'FC51', 'FC52', 'FC53', 'FC54', 'FC55', 'FC56', 'BONEPLUS', 'EDGE'],
        'SOFT_TISSUE': ['FC01', 'FC02', 'FC03', 'FC04', 'FC05'],
        'STANDARD': ['STANDARD', 'DETAIL', 'FC10', 'FC11', 'FC12', 'FC13', 'FC14', 'FC15', 'FC16', 'FC17']
    }
    
    for tissue_type, patterns in ge_patterns.items():
        for pattern in patterns:
            if kernel_upper.startswith(pattern) or kernel_upper == pattern:
                return tissue_type
    
    # Philips patterns
    philips_patterns = {
        'LUNG': ['L', 'UL'],
        'BONE': ['Y', 'YA', 'YB', 'YC', 'YD'],
        'SOFT_TISSUE': ['A', 'B'],
        'STANDARD': ['C', 'D', 'E', 'UC', 'UD', 'UE']
    }
    
    # Para Philips, kernels são geralmente 1-2 caracteres
    if len(kernel_upper) <= 3:
        for tissue_type, patterns in philips_patterns.items():
            if kernel_upper in patterns:
                return tissue_type
    
    # Canon/Toshiba patterns (similar to GE FC notation)
    canon_patterns = {
        'LUNG': ['FC30', 'FC80', 'FC81', 'FC83', 'FC85'],
        'BONE': ['FC50', 'FC51', 'FC52'],
        'SOFT_TISSUE': ['FC01', 'FC02', 'FC03', 'FC04', 'FC05'],
        'STANDARD': ['FC10', 'FC11', 'FC12', 'FC13']
    }
    
    for tissue_type, patterns in canon_patterns.items():
        for pattern in patterns:
            if kernel_upper.startswith(pattern):
                return tissue_type
    
    return 'UNKNOWN'
```

---

## 6. Estratégia de Classificação Combinada

### 6.1 Algoritmo Principal

```python
def classify_ct_series(ds):
    """
    Classifica uma série CT completa usando múltiplos critérios.
    
    Args:
        ds: pydicom Dataset
    
    Returns:
        dict: {
            'tissue_type': str,       # LUNG, BONE, SOFT_TISSUE, etc.
            'is_derived': bool,       # Se é reconstrução derivada
            'reconstruction_type': str, # MIP, MPR, 3D, ORIGINAL, etc.
            'confidence': float,      # 0.0 - 1.0
            'classification_source': str  # Campo usado para classificar
        }
    """
    result = {
        'tissue_type': 'UNKNOWN',
        'is_derived': False,
        'reconstruction_type': 'UNKNOWN',
        'confidence': 0.0,
        'classification_source': 'NONE'
    }
    
    # 1. Verificar ImageType para derivação
    image_type = getattr(ds, 'ImageType', None)
    if image_type:
        if isinstance(image_type, (list, tuple)):
            image_type = '\\'.join(image_type)
        is_derived, recon_type = is_derived_reconstruction(image_type)
        result['is_derived'] = is_derived
        result['reconstruction_type'] = recon_type
    
    # 2. Tentar classificação por ConvolutionKernel (mais confiável)
    kernel = getattr(ds, 'ConvolutionKernel', None)
    if kernel:
        if isinstance(kernel, (list, tuple)):
            kernel = kernel[0]
        manufacturer = getattr(ds, 'Manufacturer', '')
        tissue_type = classify_kernel(kernel, manufacturer)
        if tissue_type != 'UNKNOWN':
            result['tissue_type'] = tissue_type
            result['confidence'] = 0.9
            result['classification_source'] = 'ConvolutionKernel'
            return result
    
    # 3. Fallback para WindowCenter/WindowWidth
    wc = getattr(ds, 'WindowCenter', None)
    ww = getattr(ds, 'WindowWidth', None)
    
    if wc is not None and ww is not None:
        # Tratar múltiplos valores
        if isinstance(wc, (list, tuple)):
            wc = wc[0]
        if isinstance(ww, (list, tuple)):
            ww = ww[0]
        
        tissue_type = classify_window(wc, ww)
        if tissue_type != 'UNKNOWN':
            result['tissue_type'] = tissue_type
            result['confidence'] = 0.7  # Menos confiável que kernel
            result['classification_source'] = 'WindowCenter/Width'
            return result
    
    # 4. Último recurso: SeriesDescription
    desc = getattr(ds, 'SeriesDescription', '')
    if desc:
        desc_upper = desc.upper()
        desc_patterns = {
            'LUNG': ['LUNG', 'PULMO', 'HRCT', 'CHEST HIGH'],
            'BONE': ['BONE', 'OSTEO', 'SKELETAL', 'SPINE', 'ORTHO'],
            'SOFT_TISSUE': ['SOFT', 'TISSUE', 'ABDOMEN', 'PELVIS'],
            'BRAIN': ['HEAD', 'BRAIN', 'NEURO', 'CRANIAL']
        }
        
        for tissue_type, patterns in desc_patterns.items():
            for pattern in patterns:
                if pattern in desc_upper:
                    result['tissue_type'] = tissue_type
                    result['confidence'] = 0.5
                    result['classification_source'] = 'SeriesDescription'
                    return result
    
    return result
```

---

## 7. Referências e Repositórios

### 7.1 Repositórios de Código Analisados

| Repositório | URL | Componentes Relevantes |
|------------|-----|----------------------|
| **pydicom** | https://github.com/pydicom/pydicom | `src/pydicom/pixels/processing.py` - apply_windowing() |
| **dcm2niix** | https://github.com/rordenlab/dcm2niix | `console/nii_dicom.cpp` - ConvolutionKernel, ImageType handling |
| **OHIF Viewers** | https://github.com/OHIF/Viewers | CT presets (CT-Lung, CT-Bone, CT-Soft-Tissue, CT-MIP) |
| **idc-index** | https://github.com/ImagingDataCommons/idc-index | Series metadata structure |

### 7.2 Documentação de Referência

| Fonte | Descrição |
|-------|-----------|
| DICOM Standard Part 3 | Definições de atributos de imagem |
| DICOM Standard Part 6 | Dicionário de dados |
| dicom.innolitics.com | Browser interativo do padrão DICOM |
| NEMA DICOM Standard | https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.8.2.html |

### 7.3 Notas de Implementação

1. **pydicom apply_windowing()**: Implementa transformações LINEAR, LINEAR_EXACT e SIGMOID conforme DICOM VOI LUT
2. **dcm2niix**: Extrai ConvolutionKernel e ImageType para metadados BIDS JSON
3. **OHIF**: Define presets de visualização com WC/WW específicos por tipo de tecido

---

## 8. Considerações Importantes

### 8.1 Limitações

1. **Variação entre fabricantes**: Nomenclatura de kernels não é padronizada
2. **Múltiplos valores**: WindowCenter/Width podem ter múltiplos valores para diferentes presets
3. **ImageType não padronizado**: Tokens específicos variam entre implementações
4. **Reconstruções híbridas**: Algumas séries podem ter características mistas

### 8.2 Recomendações

1. **Prioridade de classificação**: ConvolutionKernel > WindowCenter/Width > SeriesDescription
2. **Validação cruzada**: Usar múltiplos critérios quando possível
3. **Configuração por site**: Kernels podem variar entre instituições para o mesmo fabricante
4. **Atualização contínua**: Novos modelos de scanners introduzem novos nomes de kernel

---

*Documento gerado com base em pesquisa de repositórios open-source de imagem médica e padrão DICOM.*
*Data: 2024*
