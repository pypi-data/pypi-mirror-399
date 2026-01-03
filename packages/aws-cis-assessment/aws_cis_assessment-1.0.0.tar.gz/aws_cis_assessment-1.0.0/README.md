# AWS CIS Controls Compliance Assessment Tool

A comprehensive tool for evaluating AWS account configurations against CIS Controls Implementation Groups (IG1, IG2, IG3) using AWS Config rule specifications without requiring AWS Config to be enabled.

## Features

- **Comprehensive Coverage**: Evaluates 100+ AWS Config rules mapped to CIS Controls
- **Implementation Groups**: Supports IG1 (Essential Cyber Hygiene), IG2 (Enhanced Security), and IG3 (Advanced Security)
- **Multiple Output Formats**: JSON, HTML, and CSV reports with detailed remediation guidance
- **No AWS Config Required**: Uses direct AWS API calls based on Config rule specifications
- **Enterprise Ready**: Handles large-scale assessments with proper error handling and performance optimization

## Quick Start

### Installation

```bash
pip install aws-cis-assessment
```

### Basic Usage

```bash
# Run assessment for all Implementation Groups
aws-cis-assess --profile my-aws-profile --regions us-east-1,us-west-2

# Run assessment for specific Implementation Group
aws-cis-assess --implementation-groups IG1 --output-format json

# Generate HTML report
aws-cis-assess --output-format html --output-file compliance-report.html
```

## Implementation Groups

### IG1 - Essential Cyber Hygiene (56 Config Rules)
- Asset Inventory and Management
- Basic Access Controls
- Secure Configuration Baselines
- Password Management

### IG2 - Enhanced Security (+30 Config Rules)
- Encryption in Transit and at Rest
- Advanced Access Controls
- Vulnerability Management
- Network Security

### IG3 - Advanced Security (+20 Config Rules)
- Sensitive Data Logging
- Network Segmentation
- Application Security
- Advanced Monitoring

## Requirements

- Python 3.8+
- AWS credentials configured (via AWS CLI, environment variables, or IAM roles)
- Read-only permissions for AWS services being assessed

## Development

```bash
# Clone repository
git clone <repository-url>
cd aws-cis-assessment

# Install development dependencies
pip install -r requirements.txt

# Run tests
pytest

# Run with coverage
pytest --cov=aws_cis_assessment

# Format code
black aws_cis_assessment/
flake8 aws_cis_assessment/
```

## License

MIT License - see LICENSE file for details.