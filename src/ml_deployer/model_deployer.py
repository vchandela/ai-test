from typing import Optional, Literal, Dict
import os
from google.cloud import aiplatform
from google.cloud import storage
import docker
import logging
from .containerization import ModelContainerizer
from .config import ConfigLoader


class MLModelDeployer:
    def __init__(self, project_id: str, region: str):
        self.project_id = project_id
        self.region = region
        self.gcs_bucket = None
        self.logger = logging.getLogger(__name__)
        self.containerizer = ModelContainerizer(project_id)

        # Initialize GCP clients
        aiplatform.init(project=project_id, location=region)
        self.storage_client = storage.Client()

    @classmethod
    def from_config(cls, config_path: str) -> "MLModelDeployer":
        """Create deployer instance from config file"""
        config = ConfigLoader.load_config(config_path)
        return cls(project_id=config["project_id"], region=config["region"])

    def validate_model(self, model_path: str) -> bool:
        """Validates if the model file exists and is in supported format"""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")

        supported_extensions = [".pkl", ".h5", "saved_model.pb"]
        return any(model_path.endswith(ext) for ext in supported_extensions)

    def upload_to_gcs(self, model_path: str, model_name: str, bucket_name: str) -> str:
        """Uploads model to Google Cloud Storage"""
        # Create bucket if it doesn't exist
        try:
            self.gcs_bucket = self.storage_client.get_bucket(bucket_name)
        except Exception:
            self.gcs_bucket = self.storage_client.create_bucket(bucket_name)

        model_dir = f"models/{model_name}"
        blob = self.gcs_bucket.blob(f"{model_dir}/{os.path.basename(model_path)}")
        blob.upload_from_filename(model_path)

        return f"gs://{bucket_name}/{model_dir}"

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
            # Build custom container if needed
            if custom_requirements:
                container_image = self.containerizer.build_vertex_ai_container(
                    model_path=model_gcs_dir,
                    framework=framework,
                    version=version,
                    custom_requirements=custom_requirements,
                )
            else:
                container_image = (
                    "us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-0:latest"
                )

            # Create model resource
            model = aiplatform.Model.upload(
                display_name=endpoint_name,
                artifact_uri=model_gcs_dir,
                serving_container_image_uri=container_image,
            )

            # Deploy model to endpoint
            endpoint = model.deploy(
                machine_type="n1-standard-2", min_replica_count=1, max_replica_count=2
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
            # Validate model
            if not self.validate_model(model_path):
                raise ValueError("Invalid model format")

            # Generate endpoint name if not provided
            if not endpoint_name:
                endpoint_name = f"model-{os.path.basename(model_path)}-endpoint"

            # Upload model to GCS
            model_gcs_dir = self.upload_to_gcs(model_path, endpoint_name, bucket_name)

            print("model_gcs_dir: ", model_gcs_dir)

            # Deploy based on target
            if deployment_target == "vertex_ai":
                return self.deploy_to_vertex(
                    model_gcs_dir=model_gcs_dir,
                    endpoint_name=endpoint_name,
                    framework=framework,
                    version=version,
                    custom_requirements=custom_requirements,
                )
            elif deployment_target == "ray":
                raise NotImplementedError("Ray deployment not yet implemented")

            return "Deployment successful"

        except Exception as e:
            self.logger.error(f"Deployment failed: {str(e)}")
            raise

    def deploy_from_config(self, config_path: str, model_path: str) -> str:
        """Deploy model using configuration file"""
        config = ConfigLoader.load_config(config_path)

        return self.deploy_model(
            model_path=model_path,
            bucket_name=config["bucket_name"],
            deployment_target=config["deployment"]["target"],
            endpoint_name=config["model_name"],
            framework=config["framework"]["name"],
            version=config["framework"]["version"],
            custom_requirements=config.get("custom_requirements"),
        )
