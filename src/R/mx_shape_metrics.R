# mx_shape_metrics.R
# Calculate skew and kurtosis for mx (fertility rate) distributions
# Metrics computed per country-year across all reproductive ages

library(data.table)

# Parse command line arguments
args <- commandArgs(trailingOnly = TRUE)
life_table_path <- args[1]
country_table_path <- args[2]

cat("LOG: Loading life_table and country_table for mx skew and kurtosis...\n")
life_table <- fread(life_table_path)
country_table <- fread(country_table_path)

cat("LOG: Calculating mx shape metrics (skew & kurtosis) for fertility...\n")

# Calculate skew and kurtosis for each country-year
# Using all ages (12- through 55+) to capture full reproductive schedule
shape_metrics <- life_table[!is.na(mx), .(
  mx_skew = sum((mx - mean(mx))^3) / ((length(mx) - 1) * sd(mx)^3),
  mx_kurtosis = sum((mx - mean(mx))^4) / ((length(mx) - 1) * sd(mx)^4)
), by = .(ISO3, ISO3_suffix, Year)]

cat(sprintf("LOG: Calculated metrics for %d country-year combinations\n", nrow(shape_metrics)))

#Merge into country_table
cat("LOG: merging mx_skew and mx_kurtosis into country table\n")
country_table <- merge(country_table, shape_metrics, 
                       by = c("ISO3", "ISO3_suffix", "Year"), 
                       all.x = TRUE)

# Save updated country_table
fwrite(country_table, country_table_path)
cat(sprintf("LOG: Updated country table saved: %s\n", country_table_path))
