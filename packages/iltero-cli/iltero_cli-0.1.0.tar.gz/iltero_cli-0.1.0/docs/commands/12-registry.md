# Registry Commands

Manage module and template registry.

## Overview

The registry stores reusable Terraform modules and templates for your organization.

## Commands

### `iltero registry modules list`

List registry modules.

```bash
iltero registry modules list

# Filter by organization
iltero registry modules list --org my-org
```

**Options:**
- `--org ORG` - Filter by organization
- `--category CATEGORY` - Filter by category
- `--output FORMAT` - Output format: `table`, `json`, `yaml`

### `iltero registry modules get`

Get module details.

```bash
iltero registry modules get my-org/vpc-module

# Specific version
iltero registry modules get my-org/vpc-module --version 1.2.0
```

### `iltero registry modules publish`

Publish a module to the registry.

```bash
iltero registry modules publish \
  --path ./my-module \
  --name vpc-module \
  --version 1.0.0 \
  --description "Production-ready VPC module"
```

**Options:**
- `--path PATH` (required) - Module path
- `--name NAME` (required) - Module name
- `--version VERSION` (required) - Semantic version
- `--description DESC` - Module description
- `--category CATEGORY` - Module category

### `iltero registry modules delete`

Delete a module version.

```bash
iltero registry modules delete my-org/vpc-module --version 1.0.0
```

## Templates

### `iltero registry templates list`

List registry templates.

```bash
iltero registry templates list
```

### `iltero registry templates get`

Get template details.

```bash
iltero registry templates get aws-vpc-template
```

### `iltero registry templates publish`

Publish a template.

```bash
iltero registry templates publish \
  --path ./template \
  --name aws-vpc-template \
  --version 1.0.0
```

## Workflow Examples

### Publish Module

```bash
# 1. Create registry token
iltero token create --name "Registry Publisher" --type registry

# 2. Prepare module
cd ./my-vpc-module

# 3. Publish to registry
iltero registry modules publish \
  --path . \
  --name vpc-module \
  --version 1.0.0 \
  --description "AWS VPC with public/private subnets" \
  --category networking
```

### Use Registry Module

```terraform
# In your Terraform code
module "vpc" {
  source  = "registry.iltero.io/my-org/vpc-module"
  version = "1.0.0"
  
  cidr_block = "10.0.0.0/16"
  azs        = ["us-east-1a", "us-east-1b"]
}
```

## See Also

- [Token Commands](token.md) - Create registry tokens
- [Organization Commands](org.md) - Manage organization

---

**Next:** [Create a registry token](token.md)
