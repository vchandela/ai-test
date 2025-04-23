from ml_deployer.model_deployer import MLModelDeployer
from ml_deployer.monitoring import ModelMonitoring
from pathlib import Path
from ml_deployer.config import ConfigLoader


def main():
    # Get config path and model path
    config_path = "configs/prod.yaml"
    models_dir = Path("models")
    model_path = models_dir / "model.pkl"

    # Deploy using config
    deployer = MLModelDeployer.from_config(config_path)
    endpoint_name = deployer.deploy_from_config(config_path, str(model_path))

    # Setup monitoring
    config = ConfigLoader.load_config(config_path)
    monitoring = ModelMonitoring(project_id=config["project_id"])
    monitoring.setup_monitoring(endpoint_name)


if __name__ == "__main__":
    main()
