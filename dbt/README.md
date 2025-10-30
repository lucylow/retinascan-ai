# dbt quickstart for RetinaScan AI

This folder contains example dbt models you can copy into a real dbt project.

Steps
1. Create a dbt project (e.g., `dbt init retinascan_dbt`).
2. Configure your profile to point at the same warehouse as `DATABASE_URL` (Postgres example):

```
# ~/.dbt/profiles.yml
retinascan_dbt:
  target: dev
  outputs:
    dev:
      type: postgres
      host: localhost
      user: user
      password: password
      dbname: retinascan
      schema: analytics
      port: 5432
```

3. Copy the SQL files from `models/` into your project's `models/` folder.
4. Run `dbt run` to build staging and marts.
