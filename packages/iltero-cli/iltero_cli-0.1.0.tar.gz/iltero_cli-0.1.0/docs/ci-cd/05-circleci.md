# CircleCI Integration

Complete guide for integrating Iltero CLI with CircleCI.

## Prerequisites

1. Create pipeline token: `iltero token create --type pipeline`
2. Add to CircleCI:
   - Go to **Project Settings** → **Environment Variables**
   - Add variable: `ILTERO_PIPELINE_TOKEN`

## Basic Config

Create `.circleci/config.yml`:

```yaml
version: 2.1

jobs:
  compliance-scan:
    docker:
      - image: cimg/python:3.11
    steps:
      - checkout
      
      - run:
          name: Install Iltero CLI
          command: pip install iltero-cli checkov
      
      - run:
          name: Run compliance scan
          command: |
            iltero scan static \
              --path ./terraform \
              --format json \
              --output scan-results.json
          environment:
            ILTERO_OUTPUT_FORMAT: json
      
      - run:
          name: Check thresholds
          command: |
            CRITICAL=$(jq '.summary.critical // 0' scan-results.json)
            if [ "$CRITICAL" -gt 0 ]; then
              echo "Found $CRITICAL critical violations"
              exit 1
            fi
      
      - store_artifacts:
          path: scan-results.json
          destination: scan-results

workflows:
  version: 2
  compliance:
    jobs:
      - compliance-scan:
          context: iltero-credentials
```

## Advanced Workflow

```yaml
version: 2.1

workflows:
  scan-and-deploy:
    jobs:
      - scan
      - upload:
          requires:
            - scan
          filters:
            branches:
              only: main

jobs:
  scan:
    docker:
      - image: cimg/python:3.11
    steps:
      - checkout
      - run: pip install iltero-cli checkov
      - run: iltero scan static --path . --format json
  
  upload:
    docker:
      - image: cimg/python:3.11
    steps:
      - checkout
      - run: pip install iltero-cli
      - run: |
          iltero scan static \
            --path . \
            --stack-id $ILTERO_STACK_ID \
            --upload
```

## See Also

- [CI/CD Overview](README.md)
- [Scan Commands](../commands/scan.md)
