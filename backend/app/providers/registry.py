from app.providers.geojson_provider import GeoJSONProvider


def get_capture_provider(provider_name: str):
    providers = {
        "geojson": GeoJSONProvider,
    }

    provider_class = providers.get(provider_name.lower())

    if provider_class is None:
        raise ValueError(f"Unsupported capture provider: {provider_name}")

    return provider_class()