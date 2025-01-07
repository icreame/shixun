from google.cloud import bigquery

client = bigquery.Client()

# Perform a query.
QUERY = (
    """
    SELECT 
  FORMAT_TIMESTAMP('%Y-%m-%d %H:%M:%S', date) AS date,
  url,
  title 
FROM 
  `gdelt-bq.gdeltv2.gqg` 
WHERE 
  date BETWEEN TIMESTAMP("2024-12-06 00:00:00") AND TIMESTAMP("2025-01-06 23:59:59")
  AND lang = 'Chinese'
  AND title LIKE '%平安银行%';
    """
    )
query_job = client.query(QUERY)  # API request
rows = query_job.result()  # Waits for query to finish

for row in rows:
    print(row.name)
