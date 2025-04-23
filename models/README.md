# Models Directory

This directory contains ML models for deployment. The system supports the following model formats:

- `.pkl` - Pickled scikit-learn models
- `.h5` - Keras/TensorFlow models
- `saved_model.pb` - TensorFlow SavedModel format

## Usage

1. Place your model file in this directory
2. Update the configuration in `configs/prod.yaml`
3. Push changes to trigger automatic deployment

## Naming Convention

- Use descriptive names for your models
- Include version information if applicable
- Example: `customer_churn_v1.pkl`

## Model Requirements

- Models should be trained and saved in one of the supported formats
- Include any custom dependencies in `configs/prod.yaml`
- Ensure model file size is within GCS limits 