# 🔍 Hallucination Detector

[![PyPI version](https://badge.fury.io/py/hallucination-detector.svg)](https://badge.fury.io/py/hallucination-detector)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Production-ready hallucination detection for LLM outputs.**

Detect, measure, and prevent AI hallucinations with confidence. Works with any LLM - OpenAI, Anthropic, open-source models, and more.

## ✨ Features

- 🎯 **Multi-Strategy Detection** - Semantic analysis, entity verification, fact-checking
- ⚡ **Production Ready** - Async support, batch processing, caching
- 📊 **Detailed Reports** - JSON, HTML, and Markdown output formats
- 🔌 **Zero Dependencies** - Core works standalone, optional enhancements available
- 🎨 **Simple API** - One line to detect, full control when needed

## 🚀 Quick Start

### Installation

```bash
# Basic installation (no dependencies)
pip install hallucination-detector

# Full installation with all features
pip install hallucination-detector[full]
```

### Basic Usage

```python
from hallucination_detector import HallucinationDetector

# Initialize detector
detector = HallucinationDetector()

# Detect hallucinations
result = detector.detect(
    response="The Eiffel Tower is located in Berlin, Germany.",
    context="The Eiffel Tower is a famous landmark in Paris, France."
)

# Check results
print(result.is_hallucination)  # True
print(result.confidence)         # 0.95
print(result.summary())
# ⚠️ 1 hallucination(s) detected
#    Confidence: 95.0%
#    Claims: 0/1 verified
```

## 📖 Documentation

### Detection Methods

#### Standard Detection

```python
from hallucination_detector import HallucinationDetector

detector = HallucinationDetector()

# With context
result = detector.detect(
    response="The CEO announced record profits of $5 billion.",
    context="The company reported annual revenue of $3 billion with modest growth."
)

# With source documents
result = detector.detect(
    response="According to the study, 80% of users prefer the new design.",
    sources=[
        "User survey results: 65% expressed preference for the new interface.",
        "Focus group findings indicated mixed reactions to the redesign."
    ]
)

# Domain-specific (stricter validation)
result = detector.detect(
    response="Take 500mg of aspirin daily for pain relief.",
    context="Recommended aspirin dosage is 75-100mg daily.",
    domain="medical",
    strict=True
)
```

#### Quick Check

```python
# Fast boolean check
if detector.quick_check(response, context):
    print("⚠️ Potential hallucination detected!")
```

#### Batch Processing

```python
# Process multiple items
results = detector.detect_batch([
    {"response": "...", "context": "..."},
    {"response": "...", "sources": ["...", "..."]},
    {"response": "...", "context": "...", "domain": "legal"},
])

for i, result in enumerate(results):
    print(f"Item {i}: {'❌' if result.is_hallucination else '✅'}")
```

### Async Support

```python
from hallucination_detector import AsyncHallucinationDetector
import asyncio

async def check_responses():
    detector = AsyncHallucinationDetector()
    
    # Single detection
    result = await detector.detect(response, context)
    
    # Batch detection
    results = await detector.detect_batch(items)
    
    return results

# Run
results = asyncio.run(check_responses())
```

### Configuration

```python
from hallucination_detector import HallucinationDetector, DetectorConfig

# Custom configuration
config = DetectorConfig(
    # Detection settings
    confidence_threshold=0.8,      # Higher = stricter
    min_claim_length=10,           # Minimum characters for a claim
    
    # Validation toggles
    enable_entity_validation=True,
    enable_temporal_validation=True,
    enable_numeric_validation=True,
    enable_semantic_validation=True,
    
    # Performance
    batch_size=32,
    max_workers=4,
    cache_embeddings=True,
    
    # Output
    include_explanations=True,
    include_suggestions=True,
    verbose=True
)

detector = HallucinationDetector(config=config)
```

### Understanding Results

```python
result = detector.detect(response, context)

# Basic info
result.is_hallucination      # bool - Any hallucinations found?
result.confidence            # float - Overall confidence (0-1)
result.total_claims          # int - Total claims extracted
result.verified_claims       # int - Claims that passed verification

# Detailed breakdown
result.hallucination_rate    # float - Percentage of hallucinated claims
result.severity_breakdown    # dict - Count by severity level
result.type_breakdown        # dict - Count by hallucination type

# Individual hallucinations
for h in result.hallucinations:
    print(f"Text: {h.text}")
    print(f"Type: {h.hallucination_type.name}")
    print(f"Severity: {h.severity.name}")
    print(f"Confidence: {h.confidence:.0%}")
    print(f"Explanation: {h.explanation}")
    print(f"Suggestion: {h.suggested_correction}")
```

### Hallucination Types

| Type | Description |
|------|-------------|
| `FACTUAL_ERROR` | Incorrect facts |
| `ENTITY_ERROR` | Wrong names, places, organizations |
| `TEMPORAL_ERROR` | Incorrect dates or times |
| `NUMERIC_ERROR` | Wrong numbers or statistics |
| `ATTRIBUTION_ERROR` | Misattributed quotes or claims |
| `FABRICATION` | Completely made-up information |
| `CONTRADICTION` | Self-contradicting statements |
| `CONTEXT_DRIFT` | Response deviates from context |
| `UNSUPPORTED_CLAIM` | Claims without evidence |
| `EXAGGERATION` | Overstated facts |

### Severity Levels

| Level | Description |
|-------|-------------|
| `LOW` | Minor inaccuracy, unlikely to cause issues |
| `MEDIUM` | Noticeable error, may mislead users |
| `HIGH` | Significant error, likely to cause problems |
| `CRITICAL` | Severe error, dangerous misinformation |

### Generating Reports

```python
from hallucination_detector import (
    DetectionReport,
    JSONReporter,
    HTMLReporter
)

# Create a report
report = DetectionReport(title="Daily Hallucination Check")

# Add results
for item in items:
    result = detector.detect(item["response"], item["context"])
    report.add_result(result)

# Print summary
print(report.summary())

# Export to JSON
json_reporter = JSONReporter(pretty=True)
json_reporter.save(report, "report.json")

# Export to HTML
html_reporter = HTMLReporter(theme="dark")
html_reporter.save(report, "report.html")
```

## 🔧 Advanced Usage

### Custom Validators

```python
from hallucination_detector.validators import FactValidator

# Add custom fact patterns
validator = FactValidator()
validator.add_false_pattern(r"COVID-19 is caused by 5G")

# Use in detector
detector = HallucinationDetector()
detector.fact_validator = validator
```

### Semantic Analysis

```python
from hallucination_detector.analyzers import SemanticAnalyzer

analyzer = SemanticAnalyzer(
    model_name="all-MiniLM-L6-v2",
    use_gpu=True,
    cache_embeddings=True
)

# Compute similarity
similarity = analyzer.compute_similarity(text1, text2)

# Check for contradictions
is_contradiction = analyzer.is_contradiction(claim, context)

# Find similar passages
matches = analyzer.find_most_similar(query, candidates, top_k=5)
```

### Entity Validation

```python
from hallucination_detector.analyzers import EntityAnalyzer

analyzer = EntityAnalyzer()

# Extract entities
entities = analyzer.extract("John works at Google in New York.")
for entity in entities:
    print(f"{entity.text}: {entity.entity_type}")
# John: PERSON
# Google: ORG  
# New York: GPE

# Verify against context
is_valid = analyzer.verify_against_context(entity, context_entities)
```

## 🏗️ Integration Examples

### With OpenAI

```python
import openai
from hallucination_detector import HallucinationDetector

detector = HallucinationDetector()

# Get completion
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": context},
        {"role": "user", "content": question}
    ]
)

# Check for hallucinations
result = detector.detect(
    response=response.choices[0].message.content,
    context=context
)

if result.is_hallucination:
    print("⚠️ Response may contain hallucinations")
    print(result.summary())
```

### With LangChain

```python
from langchain.llms import OpenAI
from hallucination_detector import HallucinationDetector

llm = OpenAI()
detector = HallucinationDetector()

def safe_generate(prompt: str, context: str) -> str:
    response = llm(prompt)
    
    result = detector.detect(response=response, context=context)
    
    if result.is_hallucination and result.confidence > 0.8:
        # Retry or flag for review
        return f"[FLAGGED] {response}"
    
    return response
```

### As Middleware

```python
from fastapi import FastAPI, HTTPException
from hallucination_detector import HallucinationDetector

app = FastAPI()
detector = HallucinationDetector()

@app.post("/generate")
async def generate(prompt: str, context: str):
    # Generate response (your LLM call)
    response = await generate_llm_response(prompt)
    
    # Check for hallucinations
    result = detector.detect(response=response, context=context)
    
    return {
        "response": response,
        "hallucination_check": {
            "passed": not result.is_hallucination,
            "confidence": result.confidence,
            "issues": len(result.hallucinations)
        }
    }
```

## 📊 Performance Tips

1. **Enable Caching**: Set `cache_embeddings=True` for repeated texts
2. **Use Batch Processing**: Process multiple items together
3. **Adjust Thresholds**: Lower thresholds for faster, less accurate checks
4. **Use Quick Check**: For high-volume, boolean-only needs
5. **GPU Acceleration**: Enable `use_gpu=True` with sentence-transformers

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md).

```bash
# Clone repository
git clone https://github.com/pranaym/hallucination-detector
cd hallucination-detector

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src tests
isort src tests
```

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

Created by **Pranay M**

---

**Found this useful?** Give it a ⭐ on [GitHub](https://github.com/pranaym/hallucination-detector)!
