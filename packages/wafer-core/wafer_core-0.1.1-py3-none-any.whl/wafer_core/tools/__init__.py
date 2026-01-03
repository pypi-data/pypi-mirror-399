"""Tools module for wafer-core.

Provides CUDA tool finding, compilation utilities, CuTeDSL analysis, and documentation queries.
"""

from wafer_core.tools.tool_finder import (
    find_nvcc,
    find_nvdisasm,
    get_nvcc_version,
    get_platform,
)
from wafer_core.tools.compiler import (
    compile_cuda,
    detect_arch,
    CompileResult,
    ArchDetectResult,
)
from wafer_core.tools.cutedsl_analyzer import (
    # Main functions
    analyze_kernel,
    diff_kernels,
    get_lineage,
    # Parsers
    parse_mlir,
    parse_ptx,
    parse_sass,
    # Feature extractors
    build_correlation_graph,
    extract_layouts,
    extract_memory_paths,
    extract_pipeline_structure,
    # Data types
    AnalysisResult,
    DiffResult,
    EntityId,
    CorrelationEdge,
    LayoutInfo,
    MemoryPath,
    PipelineStage,
    MLIROp,
    PTXInstruction,
    SASSInstruction,
    ParsedMLIR,
    ParsedPTX,
    ParsedSASS,
)
from wafer_core.tools.docs import (
    search_docs,
    query_docs,
    DocsSearchResult,
    DocsSearchResponse,
    DocsRAGChunk,
)

__all__ = [
    # Tool finder
    "find_nvcc",
    "find_nvdisasm",
    "get_nvcc_version",
    "get_platform",
    # Compiler
    "compile_cuda",
    "detect_arch",
    "CompileResult",
    "ArchDetectResult",
    # CuTeDSL Analyzer - Functions
    "analyze_kernel",
    "diff_kernels",
    "get_lineage",
    "parse_mlir",
    "parse_ptx",
    "parse_sass",
    "build_correlation_graph",
    "extract_layouts",
    "extract_memory_paths",
    "extract_pipeline_structure",
    # CuTeDSL Analyzer - Types
    "AnalysisResult",
    "DiffResult",
    "EntityId",
    "CorrelationEdge",
    "LayoutInfo",
    "MemoryPath",
    "PipelineStage",
    "MLIROp",
    "PTXInstruction",
    "SASSInstruction",
    "ParsedMLIR",
    "ParsedPTX",
    "ParsedSASS",
    # Docs - Functions
    "search_docs",
    "query_docs",
    # Docs - Types
    "DocsSearchResult",
    "DocsSearchResponse",
    "DocsRAGChunk",
]
