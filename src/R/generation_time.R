args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2) stop("usage: Rscript <script_path.R> <life_table_path.csv> <country_table_path.csv>")
life_table_path <- args[1]
country_table_path <- args[2]

# read csv
life <- read.csv(life_table_path, header = TRUE)
country <- read.csv(country_table_path, header = TRUE)

# coerce numeric fields
#life$Age <- as.numeric(life$Age)
#life$lx <- as.numeric(life$lx)
#life$mx <- as.numeric(life$mx)

# split into (country, year) groups
groups <- split(seq_len(nrow(life)), interaction(life$ISO3, life$Year, drop = TRUE))

# compute generation time (T) per group
gen_list <- lapply(groups, function(g) {
  x <- life$Age[g]
  px <- life$px[g]
  
  # Lotka T = sum(x * px) / sum(px)
  numerator <- sum(x * px, na.rm = TRUE)
  denominator <- sum(px, na.rm = TRUE)
  T <- numerator / denominator
  
  data.frame(
    ISO3 = life$ISO3[g[1]],
    Year = life$Year[g[1]],
    T = T,
    stringsAsFactors = FALSE
  )
})
gen_df <- do.call(rbind, gen_list)

# merge into country table
out <- merge(country, gen_df, by = c("ISO3", "Year"), all = TRUE)
out <- out[order(out$ISO3, out$Year), ]

# write csv
write.csv(out, country_table_path, row.names = FALSE)