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