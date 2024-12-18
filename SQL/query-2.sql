# Maximum and Minimum Temperature per City
SELECT 
    City,
    MAX(Temperature) AS "Max. Temperature",
    MIN(Temperature) AS "Min. Temperature"
FROM proj_database.open_meteo_weather_data_parquet_tbl_prod_2024_12_18_14_56_21_565756
GROUP BY City
ORDER BY City;
