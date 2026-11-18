from statistics import mean, pstdev


def detect_ndvi_anomalies(
    observations: list[dict],
    z_threshold: float = 2.0,
):
    values = [
        observation["mean"]
        for observation in observations
        if observation.get("mean") is not None
    ]

    if len(values) < 4:
        return {
            "status": "insufficient_data",
            "message": "At least four observations are required.",
            "anomalies": [],
        }

    average = mean(values)
    deviation = pstdev(values)

    if deviation == 0:
        return {
            "status": "no_variation",
            "message": "All observations have the same mean NDVI.",
            "anomalies": [],
        }

    anomalies = []

    for observation in observations:
        value = observation.get("mean")

        if value is None:
            continue

        z_score = (value - average) / deviation

        if abs(z_score) >= z_threshold:
            anomalies.append({
                "dataset_id": str(observation["dataset_id"]),
                "capture_id": str(observation["capture_id"]),
                "acquisition_date": (
                    observation["acquisition_date"].isoformat()
                    if hasattr(observation["acquisition_date"], "isoformat")
                    else str(observation["acquisition_date"])
                ),
                "mean_ndvi": value,
                "z_score": round(z_score, 3),
                "direction": (
                    "unusually_low"
                    if z_score < 0
                    else "unusually_high"
                ),
            })

    return {
        "status": "completed",
        "average_ndvi": average,
        "standard_deviation": deviation,
        "threshold": z_threshold,
        "anomalies": anomalies,
    }