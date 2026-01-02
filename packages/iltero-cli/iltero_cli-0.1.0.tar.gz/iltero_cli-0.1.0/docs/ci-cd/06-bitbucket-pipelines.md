# Bitbucket Pipelines Integration

Complete guide for integrating Iltero CLI with Bitbucket Pipelines.

## Prerequisites

1. Create pipeline token: `iltero token create --type pipeline`
2. Add to Bitbucket:
   - Go to **Repository Settings** → **Pipelines** → **Repository variables**
   - Add variable: `ILTERO_PIPELINE_TOKEN`
   - Mark as **Secured**

## Basic Pipeline

Create `bitbucket-pipelines.yml`:

```yaml
image: python:3.11

pipelines:
  pull-requests:
    '**':
      - step:
          name: Compliance Scan
          caches:
            - pip
          script:
            - pip install iltero-cli checkov
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
            - scan-results.json
  
  branches:
    main:
      - step:
          name: Scan and Upload
          caches:
            - pip
          script:
            - pip install iltero-cli checkov
            - |
              iltero scan static \
                --path ./terraform \
                --stack-id ${ILTERO_STACK_ID} \
                --upload \
                --format sarif \
                --output iltero.sarif
          artifacts:
            - iltero.sarif
```

## Custom Pipeline

```yaml
definitions:
  steps:
    - step: &scan
        name: Compliance Scan
        image: python:3.11
        caches:
          - pip
        script:
          - pip install iltero-cli checkov
          - iltero scan static --path . --format json

pipelines:
  custom:
    manual-scan:
      - step: *scan
  
  pull-requests:
    '**':
      - step: *scan
```

## See Also

- [CI/CD Overview](README.md)
- [Scan Commands](../commands/scan.md)
