import os
import docker
import logging
from typing import Optional, Dict
from pathlib import Path


class ModelContainerizer:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.client = docker.from_env()
        self.logger = logging.getLogger(__name__)

    def build_vertex_ai_container(
        self,
        model_path: str,
        framework: str = "sklearn",
        version: str = "1.0",
        custom_requirements: Optional[Dict[str, str]] = None,
    ) -> str:
        """Builds a container image for Vertex AI deployment"""
        try:
            # Create temporary directory for Docker build context
            build_context = Path("build")
            build_context.mkdir(exist_ok=True)

            # Create Dockerfile
            dockerfile_content = self._generate_vertex_dockerfile(
                framework=framework,
                version=version,
                custom_requirements=custom_requirements,
            )

            with open(build_context / "Dockerfile", "w") as f:
                f.write(dockerfile_content)

            # Copy model file
            os.system(f"cp {model_path} {build_context}/model")

            # Build image
            image_name = f"gcr.io/{self.project_id}/vertex-ai-model:{version}"
            self.client.images.build(path=str(build_context), tag=image_name, rm=True)

            # Push to GCR
            self.client.images.push(image_name)

            return image_name

        except Exception as e:
            self.logger.error(f"Container build failed: {str(e)}")
            raise
        finally:
            # Cleanup
            if build_context.exists():
                os.system(f"rm -rf {build_context}")

    def _generate_vertex_dockerfile(
        self,
        framework: str,
        version: str,
        custom_requirements: Optional[Dict[str, str]] = None,
    ) -> str:
        """Generates Dockerfile for Vertex AI deployment"""
        base_image = f"gcr.io/cloud-aiplatform/prediction/{framework}-cpu:{version}"

        dockerfile = f"""
FROM {base_image}

WORKDIR /app

# Copy model
COPY model /app/model

# Install custom requirements if any
"""
        if custom_requirements:
            requirements = "\n".join(
                [f"{pkg}=={ver}" for pkg, ver in custom_requirements.items()]
            )
            dockerfile += f"""
RUN pip install {requirements}
"""

        return dockerfile
