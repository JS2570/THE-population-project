args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2) stop("usage: Rscript <script_path.R> <life_table_path.csv> <country_table_path.csv>")
life_table_path <- args[1]
country_table_path <- args[2]

# read csv
life <- read.csv(life_table_path, header = TRUE)
country <- read.csv(country_table_path, header = TRUE)

# split into (country, year) groups
groups <- split(seq_len(nrow(life)), interaction(life$ISO3, life$Year, drop = TRUE))

ne_list <- lapply(groups, function(g) {
  iso <- life$ISO3[g[1]]
  year <- life$Year[g[1]]
  
  # index N1 where age == 1
  #i <- which(life$Age[g] == 1)
  #N1 <- life$lx[g][i[1]]
  N1 <- 1 # relative N1 until we have age-1 census
  
  # T from country table for the same ISO3 and year
  match_row <- which(country$ISO3 == iso & country$Year == year)
  T <- country$T[match_row[1]]
                 
  lx <- life$lx[g]
  sx <- life$sx[g]
  dx <- life$dx[g]
  vx <- life$vx[g]
  
  # Ne = (N1 * T) / sum(lx * sx * dx * v(x + 1)^2)
  numerator <- N1 * T
  
  # compute terms, keeping only rows where every factor is finite
  vx_next <- vx[-1]
  ok <- is.finite(lx) & is.finite(sx) & is.finite(dx) & is.finite(vx_next)
  term <- lx[ok] * sx[ok] * dx[ok]* vx_next[ok]^2
  denominator <- sum(term, na.rm = TRUE)

  Ne <- numerator / denominator
  
  data.frame(
    ISO3 = iso,
    Year = year,
    Ne = Ne,
    stringsAsFactors = FALSE
  )
})
Ne_df <- do.call(rbind, ne_list)

# merge into country table
out <- merge(country, Ne_df, by = c("ISO3", "Year"), all = TRUE)
out <- out[order(out$ISO3, out$Year), ]

# write csv
write.csv(out, country_table_path, row.names = FALSE)