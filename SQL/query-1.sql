# Temperature Throughout a Day per City
SELECT 
    City,
    CAST(CONCAT(Date, ' ', Time) AS TIMESTAMP) AS datetime,
    ROUND(AVG(Temperature), 2) AS "Avg. Temperature"
FROM proj_database.open_meteo_weather_data_parquet_tbl_prod_2024_12_18_14_56_21_565756
WHERE Date = '2024-12-18'
GROUP BY City, Date, Time
ORDER BY datetime, City;
