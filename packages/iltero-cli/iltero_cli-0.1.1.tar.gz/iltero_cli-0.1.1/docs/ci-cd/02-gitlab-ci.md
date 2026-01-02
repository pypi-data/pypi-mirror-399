# GitLab CI Integration

Complete guide for integrating Iltero CLI with GitLab CI/CD.

## Prerequisites

1. Create pipeline token: `iltero token create --type pipeline`
2. Add to GitLab CI/CD variables:
   - Go to **Settings** → **CI/CD** → **Variables**
   - Add variable: `ILTERO_PIPELINE_TOKEN`
   - Mark as **Protected** and **Masked**

## Basic Pipeline

Create `.gitlab-ci.yml`:

```yaml
stages:
  - scan

variables:
  ILTERO_OUTPUT_FORMAT: json
  ILTERO_NO_COLOR: "true"

compliance-scan:
  stage: scan
  image: python:3.11
  before_script:
    - pip install iltero-cli checkov
  script:
    - |
      iltero scan static \
        --path ./terraform \
        --format json \
        --output scan-results.json
    
    - |
      CRITICAL=$(jq '.summary.critical // 0' scan-results.json)
      if [ "$CRITICAL" -gt 0 ]; then
        echo "❌ Found $CRITICAL critical violations"
        exit 1
      fi
  artifacts:
    paths:
      - scan-results.json
    expire_in: 30 days
  only:
    - merge_requests
    - main
```

## Multi-Stage Pipeline

```yaml
stages:
  - validate
  - scan
  - upload

validate:
  stage: validate
  image: python:3.11
  script:
    - pip install iltero-cli checkov
    - iltero scanner check
  only:
    - merge_requests
    - main

scan:
  stage: scan
  image: python:3.11
  script:
    - pip install iltero-cli checkov
    - iltero scan static --path . --format json --output results.json
  artifacts:
    paths:
      - results.json

upload:
  stage: upload
  image: python:3.11
  dependencies:
    - scan
  script:
    - pip install iltero-cli
    - |
      iltero scan static \
        --path . \
        --stack-id ${ILTERO_STACK_ID} \
        --upload
  only:
    - main
```

## JUnit Report Integration

```yaml
compliance-scan:
  stage: scan
  image: python:3.11
  script:
    - pip install iltero-cli checkov
    - iltero scan static --path . --format junit --output results.xml
  artifacts:
    reports:
      junit: results.xml
```

## See Also

- [CI/CD Overview](README.md)
- [Scan Commands](../commands/scan.md)
