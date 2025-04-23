from google.cloud import monitoring_v3
from google.cloud.monitoring_v3 import MetricServiceClient
import time


class ModelMonitoring:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.client = monitoring_v3.MetricServiceClient()
        self.project_name = f"projects/{project_id}"

    def setup_monitoring(self, endpoint_name: str):
        """Sets up basic monitoring for the deployed endpoint"""
        # Create custom metrics
        descriptor = monitoring_v3.MetricDescriptor(
            type_="custom.googleapis.com/ml/model/prediction_latency",
            metric_kind=monitoring_v3.MetricDescriptor.MetricKind.GAUGE,
            value_type=monitoring_v3.MetricDescriptor.ValueType.DOUBLE,
            description="Model prediction latency",
        )

        self.client.create_metric_descriptor(
            name=self.project_name, metric_descriptor=descriptor
        )
