from huggingface_hub import HfApi
hf_api = HfApi()
models = hf_api.list_models(filter="text-generation", sort="downloads", direction=-1, limit=5)
models_list = list(models)
# Print first 5 models
for model in models_list[:5]:
    print(model.modelId)