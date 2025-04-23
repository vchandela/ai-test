# Configurations Directory

This directory contains deployment configurations for different environments.

## Files

- `prod.yaml` - Production environment configuration
- `dev.yaml` - Development environment configuration (optional)

## Configuration Options

### Required Fields
- `model_name`: Name of the model
- `project_id`: GCP project ID
- `region`: Deployment region
- `deployment`: Deployment configuration
  - `target`: Deployment target (vertex_ai or ray)
  - `machine_type`: GCP machine type
  - `min_replicas`: Minimum number of replicas
  - `max_replicas`: Maximum number of replicas

### Optional Fields
- `framework`: ML framework configuration
  - `name`: Framework name (e.g., sklearn)
  - `version`: Framework version
- `custom_requirements`: Additional pip requirements
``` 