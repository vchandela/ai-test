from typing import Optional, Literal, Dict
import os
from google.cloud import aiplatform
from google.cloud import storage
import docker
import logging
from .containerization import ModelContainerizer
from .config import ConfigLoader
from .logging_config import setup_logging


class MLModelDeployer:
    def __init__(self, project_id: str, region: str):
        self.project_id = project_id
        self.region = region
        self.gcs_bucket = None
        self.logger = logging.getLogger(__name__)
        self.containerizer = ModelContainerizer(project_id)

        # Initialize GCP clients
        self.logger.info(
            f"Initializing GCP clients for project {project_id} in region {region}"
        )
        aiplatform.init(project=project_id, location=region)
        self.storage_client = storage.Client()

    @classmethod
    def from_config(cls, config_path: str) -> "MLModelDeployer":
        """Create deployer instance from config file"""
        config = ConfigLoader.load_config(config_path)
        instance = cls(project_id=config["project_id"], region=config["region"])
        instance.logger.info(f"Deployer instance created with config: {config}")
        return instance

    def validate_model(self, model_path: str) -> bool:
        """Validates if the model file exists and is in supported format"""
        self.logger.info(f"Validating model at path: {model_path}")
        if not os.path.exists(model_path):
            self.logger.error(f"Model file not found: {model_path}")
            raise FileNotFoundError(f"Model file not found: {model_path}")

        supported_extensions = [".pkl", ".h5", "saved_model.pb"]
        is_valid = any(model_path.endswith(ext) for ext in supported_extensions)
        if is_valid:
            self.logger.info(f"Model validation successful for {model_path}")
        else:
            self.logger.error(f"Unsupported model format for {model_path}")
        return is_valid

    def upload_to_gcs(self, model_path: str, model_name: str, bucket_name: str) -> str:
        """Uploads model to Google Cloud Storage"""
        self.logger.info(
            f"Starting GCS upload for model {model_name} to bucket {bucket_name}"
        )

        # Create bucket if it doesn't exist
        try:
            self.logger.info(f"Checking if bucket {bucket_name} exists")
            self.gcs_bucket = self.storage_client.get_bucket(bucket_name)
            self.logger.info(f"Bucket {bucket_name} exists")
        except Exception as e:
            self.logger.info(
                f"Bucket {bucket_name} does not exist, creating new bucket"
            )
            self.gcs_bucket = self.storage_client.create_bucket(bucket_name)
            self.logger.info(f"Created new bucket {bucket_name}")

        model_dir = f"models/{model_name}"
        blob = self.gcs_bucket.blob(f"{model_dir}/{os.path.basename(model_path)}")

        self.logger.info(
            f"Uploading model to GCS path: {model_dir}/{os.path.basename(model_path)}"
        )
        blob.upload_from_filename(model_path)
        self.logger.info("Model upload completed successfully")

        gcs_path = f"gs://{bucket_name}/{model_dir}"
        self.logger.info(f"Model available at GCS path: {gcs_path}")
        return gcs_path

    def deploy_to_vertex(
        self,
        model_gcs_dir: str,
        endpoint_name: str,
        framework: str = "sklearn",
        version: str = "1.0",
        custom_requirements: Optional[Dict[str, str]] = None,
    ) -> str:
        """Deploys model to Vertex AI"""
        try:
            self.logger.info(
                f"Starting Vertex AI deployment for model at {model_gcs_dir}"
            )

            # Build custom container if needed
            if custom_requirements:
                self.logger.info("Building custom container with requirements")
                container_image = self.containerizer.build_vertex_ai_container(
                    model_path=model_gcs_dir,
                    framework=framework,
                    version=version,
                    custom_requirements=custom_requirements,
                )
                self.logger.info(f"Custom container built: {container_image}")
            else:
                container_image = (
                    f"us-docker.pkg.dev/vertex-ai/prediction/{framework}-cpu.{version}:latest"
                )
                self.logger.info(f"Using default container image: {container_image}")

            # Create model resource
            self.logger.info(
                f"Uploading model to Vertex AI with display name: {endpoint_name}"
            )
            model = aiplatform.Model.upload(
                display_name=endpoint_name,
                artifact_uri=model_gcs_dir,
                serving_container_image_uri=container_image,
            )
            self.logger.info(
                f"Model uploaded successfully. Resource name: {model.resource_name}"
            )

            # Deploy model to endpoint
            self.logger.info("Starting model deployment to endpoint")
            endpoint = model.deploy(
                machine_type="n1-standard-2", min_replica_count=1, max_replica_count=2
            )
            self.logger.info(
                f"Model deployed successfully. Endpoint: {endpoint.resource_name}"
            )

            return endpoint.resource_name

        except Exception as e:
            self.logger.error(f"Vertex AI deployment failed: {str(e)}")
            raise

    def deploy_model(
        self,
        model_path: str,
        bucket_name: str,
        deployment_target: Literal["vertex_ai", "ray"],
        endpoint_name: Optional[str] = None,
        framework: str = "sklearn",
        version: str = "1.0",
        custom_requirements: Optional[Dict[str, str]] = None,
    ) -> str:
        """Main deployment orchestrator"""
        try:
            self.logger.info(f"Starting deployment process for model: {model_path}")

            # Validate model
            if not self.validate_model(model_path):
                raise ValueError("Invalid model format")

            # Generate endpoint name if not provided
            if not endpoint_name:
                endpoint_name = f"model-{os.path.basename(model_path)}-endpoint"
                self.logger.info(f"Generated endpoint name: {endpoint_name}")

            # Upload model to GCS
            self.logger.info(f"Uploading model to GCS bucket: {bucket_name}")
            model_gcs_dir = self.upload_to_gcs(model_path, endpoint_name, bucket_name)

            # Deploy based on target
            if deployment_target == "vertex_ai":
                self.logger.info("Deploying to Vertex AI")
                return self.deploy_to_vertex(
                    model_gcs_dir=model_gcs_dir,
                    endpoint_name=endpoint_name,
                    framework=framework,
                    version=version,
                    custom_requirements=custom_requirements,
                )
            elif deployment_target == "ray":
                self.logger.error("Ray deployment not yet implemented")
                raise NotImplementedError("Ray deployment not yet implemented")

            return "Deployment successful"

        except Exception as e:
            self.logger.error(f"Deployment failed: {str(e)}")
            raise

    def deploy_from_config(self, config_path: str, model_path: str) -> str:
        """Deploy model using configuration file"""
        self.logger.info(f"Loading deployment configuration from {config_path}")
        config = ConfigLoader.load_config(config_path)

        self.logger.info("Starting deployment from config")
        return self.deploy_model(
            model_path=model_path,
            bucket_name=config["bucket_name"],
            deployment_target=config["deployment"]["target"],
            endpoint_name=config["model_name"],
            framework=config["framework"]["name"],
            version=config["framework"]["version"],
            custom_requirements=config.get("custom_requirements"),
        )
