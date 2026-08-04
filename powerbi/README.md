# Power BI

This folder documents the Power BI handoff area for the project.

Power BI should consume stable PostgreSQL tables from the `powerbi` schema, created by dbt models under `dbt/models/marts/powerbi/`.

Recommended contents for later days:

- PBIX file notes or version log
- Power BI connection instructions
- Dataset/table mapping from dbt `powerbi` marts
- Refresh assumptions and known limitations

Do not store credentials or local connection secrets in this folder.
