# ML Model Deployment System

A flexible ML model deployment system that supports deploying models to GCP services (Vertex AI and Ray).

## Features

- Model validation and versioning
- GCS integration for model storage
- Vertex AI deployment support
- Extensible architecture for Ray deployment
- Monitoring setup
- CI/CD integration

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-org/pavo.git
cd pavo
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up GCP credentials for local deelopment:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-key.json"
```

## CI/CD

The project includes a GitHub Actions workflow for automated deployment. To use it:

1. Add your GCP service account key as a secret named `GCP_SA_KEY`
2. Push changes to the `models/` or `configs/` directories to trigger deployment

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

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