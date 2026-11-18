def vegetation_analysis_prompt(
    project_id: str,
    start_date: str,
    end_date: str,
) -> str:
    return f"""
Analyse vegetation conditions for Aleph Next project {project_id}.

Analysis period:
Start: {start_date}
End: {end_date}

Use the project's actual NDVI observations.

Include:
1. Overall vegetation trend.
2. Changes between available observation dates.
3. Unusual statistical observations.
4. Data coverage and limitations.
5. Recommendations for further investigation.

Do not invent satellite measurements or environmental causes.
Clearly distinguish measured values from interpretation.
"""


def environmental_report_prompt(
    project_id: str,
) -> str:
    return f"""
Prepare an environmental monitoring report for project {project_id}.

Use only verified project observations and statistics.

Include:
1. Executive summary.
2. Satellite data coverage.
3. NDVI analysis.
4. Observed changes.
5. Data limitations.
6. Recommendations.
"""