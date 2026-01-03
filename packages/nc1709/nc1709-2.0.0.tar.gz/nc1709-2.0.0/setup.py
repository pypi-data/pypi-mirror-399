"""
NC1709 Enhanced - Setup configuration
Combines NC1709 with ECHO's advanced local LLM features
"""

from setuptools import setup, find_packages

# Read README if available
long_description = """
# NC1709 Enhanced

An advanced AI assistant that combines:
- NC1709's comprehensive CLI features
- ECHO's cognitive architecture and local LLM optimization
- Performance benchmarking and intelligent model routing
- Support for latest 2025 models (Codestral, Qwen3, DeepSeek-R1)

## Features

- **Hybrid Mode**: Seamlessly switch between local and remote processing
- **Cognitive System**: 5-layer cognitive architecture for complex tasks
- **Performance Benchmarking**: Compare and optimize model performance
- **Intelligent Routing**: Automatic model selection based on task complexity
- **2025 Models**: Support for cutting-edge models like DeepSeek-R1 with o1-style reasoning

## Installation

```bash
pip install nc1709-enhanced
```

## Usage

```bash
# Run in local mode (default)
nc1709-enhanced

# Run in hybrid mode (auto-select local/remote)
nc1709-enhanced --mode hybrid

# Run performance benchmark
nc1709-enhanced --benchmark
```
"""

# Core requirements combining both systems
install_requires = [
    # NC1709 core requirements
    "litellm>=1.0.0",
    "rich>=13.0.0",
    "prompt_toolkit>=3.0.0",
    "packaging>=21.0",
    "click>=8.1.0",
    "ddgs>=9.0.0",
    
    # ECHO requirements
    "ollama>=0.1.0",
    "httpx>=0.24.0",
    "aiofiles>=23.0.0",
    "psutil>=5.9.0",
    
    # Shared requirements
    "pydantic>=2.0.0",
    "python-dotenv>=0.20.0",
    "asyncio>=3.4.3",
]

# Optional requirements for advanced features
extras_require = {
    "memory": [
        "chromadb>=0.4.0",
        "sentence-transformers>=2.2.0",
    ],
    "dev": [
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
        "black>=23.0.0",
        "isort>=5.12.0",
        "mypy>=1.0.0",
    ],
    "performance": [
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "matplotlib>=3.7.0",
    ],
}

setup(
    name="nc1709",
    version="2.0.0",
    author="NC1709 Team + ECHO Enhancement",
    author_email="support@lafzusa.com",
    description="Advanced AI assistant combining NC1709 with ECHO's cognitive architecture",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/nc1709-enhanced",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            "nc1709-enhanced=nc1709_enhanced.cli_enhanced:main",
            "nc1709=nc1709_enhanced.cli:main",  # Keep original CLI
            "nc1709-benchmark=nc1709_enhanced.performance.benchmark:main",
        ],
    },
    include_package_data=True,
    package_data={
        "nc1709_enhanced": [
            "prompts/*.txt",
            "prompts/*.md",
            "config/*.json",
            "models/*.json",
        ],
    },
)