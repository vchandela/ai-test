from ml_deployer.model_deployer import MLModelDeployer
from ml_deployer.monitoring import ModelMonitoring
from pathlib import Path
from ml_deployer.config import ConfigLoader
from ml_deployer.logging_config import setup_logging
import logging


def main():
    # Setup logging
    logger = setup_logging()
    logger.info("Starting model deployment process")

    # Get config path and model path
    config_path = "configs/prod.yaml"
    models_dir = Path("models")
    model_path = models_dir / "model.pkl"

    logger.info(f"Using configuration from: {config_path}")
    logger.info(f"Model path: {model_path}")

    try:
        # Deploy using config
        logger.info("Initializing model deployer")
        deployer = MLModelDeployer.from_config(config_path)
        logger.info("Starting model deployment")
        endpoint_name = deployer.deploy_from_config(config_path, str(model_path))
        logger.info(f"Model deployed successfully. Endpoint: {endpoint_name}")

        # Setup monitoring
        logger.info("Setting up monitoring")
        config = ConfigLoader.load_config(config_path)
        monitoring = ModelMonitoring(project_id=config["project_id"])
        monitoring.setup_monitoring(endpoint_name)
        logger.info("Monitoring setup completed")

    except Exception as e:
        logger.error(f"Deployment failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
