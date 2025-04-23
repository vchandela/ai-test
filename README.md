# ML Model Deployment System

A flexible ML model deployment system that supports deploying models to GCP services (Vertex AI and Ray).

## Features

- Model validation and versioning
- GCS integration for model storage
- Vertex AI deployment support
- Extensible architecture for Ray deployment
- Monitoring setup
- CI/CD integration
- Logging

## How it works
- check if the model path is valid -- directory with `.pkl` or `SavedModel` file
- upload the model artifact to GCS
- `deployment_target` -- `vertex_ai` or `ray` (TBD)
  - for vertex AI, create a custom container (using Docker) or a built-in container.
    - For this demo, I've used `us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-0:latest`
    - Vertex AI basically loads the model artifact to a container and exposes HTTP endpoints that we can use for inference. All the auto-scaling and security is handled automatically.
- for CI/CD, we can use Github Actions. It will notice any changes in `models/` and `configs/` and start a new deployment
- for logging, we are using both `stdout` and `logs` folder
- for monitoring, we can use the cloud monitoring provide by GCP. In future, we can have custom monitoring or also integrate Grafana.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/vchandela/ai-test.git
cd ai-test
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up GCP credentials for local development:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-key.json"
```

4. Run the code
```bash
python src/example.py
```

## CI/CD

The project includes a GitHub Actions workflow for automated deployment. To use it:

1. Add your GCP service account key as a secret named `GCP_SA_KEY`
2. Push changes to the `models/` or `configs/` directories to trigger deployment

## License

MIT License

## Logging

The system uses a dual-logging approach for comprehensive tracking and debugging:

### Terminal Output
- Real-time deployment progress
- Simplified format: `LEVEL - Message`
- Immediate feedback during execution
- Example: `INFO - Starting deployment process`

### Log File (`logs/deployment.log`)
- Permanent record of all deployments
- Detailed format: `Timestamp - Module - Level - Message`
- Example: `2024-04-23 14:30:22 - ml_deployer - INFO - Starting deployment process`
- Useful for:
  - Debugging issues
  - Audit trails
  - Historical tracking
  - Support and troubleshooting

### How It Works
The logging system broadcasts each message to two independent handlers:
```python
logger.info("Message")
         │
         ├─────► Console Handler ──────► Terminal
         │
         └─────► File Handler ─────────► logs/deployment.log
```

Each handler applies its own formatting and writes to its destination. This ensures both immediate visibility (terminal) and permanent record-keeping (log file).

### Log Levels
- INFO: Normal operation events
- ERROR: Issues that need attention
- WARNING: Potential issues
- DEBUG: Detailed information (if enabled)

### Usage
Logs are automatically created in the `logs` directory. No additional setup is required. 