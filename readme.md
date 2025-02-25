# AI Capability Review Tool

> **Note:** This project is a work in progress. Functionality and documentation will be improved over time.

## Overview

The AI Capability Review Tool automates the process of evaluating software vendors' AI capabilities by analyzing their documentation to answer key questions about privacy, data usage, opt-out mechanisms, and AI implementation details.

This tool helps security and compliance professionals quickly assess:
- Whether AI functionality can be disabled or opted out of
- If opt-out controls are available at the enterprise level
- Whether AI capabilities are native or provided by third parties
- How user data is retained and used for AI/ML model training
- If models trained on user data are shared with other users
- Whether contractual protections exist for third-party AI providers
- Other potential concerns in vendor documentation

<video width="640" height="360" controls>
  <source src="v01_vid.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>


## Current Status

This tool is currently under development. Key features implemented:
- Comprehensive document scraping from vendor websites
- Multiple document type identification and analysis
- AI capability detection and assessment
- Confidence scoring for findings
- Support for major cloud/SaaS vendors

Areas still being improved:
- Enhancing pattern matching accuracy
- Improving confidence level calculation
- Refining the analysis algorithm
- Expanding the vendor database

## How to Use

### Prerequisites

- Python 3.8 or higher
- Required packages: requests, beautifulsoup4, pandas, re

### Installation

1. Clone this repository:
   ```
   git clone [repository-url]
   cd ai-capability-review
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

### Basic Usage

```python
from ai_review import get_vendor_documentation, extract_document_text, fix_analyze_ai_capabilities, direct_confidence_fix

def review_vendor(vendor_url):
    # Get document URLs
    doc_urls = get_vendor_documentation(vendor_url)
    
    # Extract text from each document
    doc_texts = {}
    for doc_type, url in doc_urls.items():
        if url:
            try:
                print(f"Extracting {doc_type}: {url}")
                doc_texts[doc_type] = extract_document_text(url)
            except Exception as e:
                print(f"Error extracting {doc_type}: {str(e)}")
    
    # Analyze AI capabilities
    analysis = fix_analyze_ai_capabilities(doc_texts)
    
    # Apply confidence score fix
    analysis = direct_confidence_fix(analysis)
    
    return analysis

# Example: Review Microsoft
result = review_vendor("https://www.microsoft.com")
print(result)
```

### Example Output

```json
{
  "opt_out_available": true,
  "enterprise_opt_out": true,
  "native_ai": false,
  "third_party_providers": ["OpenAI", "Azure"],
  "data_retention": true,
  "model_training": true,
  "model_sharing": false,
  "contractual_protections": true,
  "confidence_levels": {
    "opt_out_available": 0.7,
    "enterprise_opt_out": 0.6,
    "native_ai": 0.8,
    "third_party_providers": 0.9,
    "data_retention": 0.7,
    "model_training": 0.8,
    "model_sharing": 0.6,
    "contractual_protections": 0.7
  },
  "concerns": [
    "Potential concern: Data retention period not clearly specified",
    "Potential concern: Unclear process for enterprise-wide opt-out"
  ]
}
```

## Key Components

- **Document Discovery**: Automatically finds and collects relevant documentation from vendor websites.
- **Document Analysis**: Processes multiple document types looking for evidence of AI capabilities.
- **Pattern Matching**: Uses regular expressions to identify relevant information about AI usage and controls.
- **Confidence Scoring**: Assigns confidence levels to findings based on evidence strength.

## Supported Document Types

The tool searches for and analyzes many document types, including:
- Privacy policies
- Terms of service
- Data processing agreements
- AI trust/ethics documentation
- Responsible AI documentation
- Data security information
- GDPR/CCPA compliance documentation
- Acceptable use policies
- Data retention policies
- Subprocessor lists
- API terms
- Developer policies
- Admin guides
- Enterprise controls




