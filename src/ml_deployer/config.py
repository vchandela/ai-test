import yaml
from typing import Dict, Any
from pathlib import Path


class ConfigLoader:
    @staticmethod
    def load_config(config_path: str) -> Dict[str, Any]:
        """Load deployment configuration from yaml file"""
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        required_fields = [
            "model_name",
            "project_id",
            "region",
            "deployment",
            "bucket_name",
        ]
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field in config: {field}")

        return config
