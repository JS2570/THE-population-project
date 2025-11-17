args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1) stop("usage: Rscript <script_path.R> <path.csv>")
path <- args[1]

# read csv
df <- read.csv(path, header = TRUE)

# require these columns
required <- c("ISO3", "Year", "Age", "lx", "mx")
missing <- setdiff(required, names(df))
if (length(missing) > 0) {
  stop("missing required columns: ", paste(missing, collapse = ", "))
}

# initialise
n <- nrow(df)
df$dx <- NA
df$N <- NA
df$sx <- NA
df$lxmx_STAND <- NA
df$vx <- NA
df$lxmx_STAND_SUM_qx <- NA

#calculate and store N for all rows 
df$N <- df$lx * 1000 


groups <- split(seq_len(n), paste(df$ISO3, df$ISO3_suffix, df$Year), sep=":")
#diagnosing - seeing if germeny is doubling denominator on lxmx_stand
for (group_name in names(groups)) {
  g <- groups[[group_name]]
  cat("Group:", group_name, "has", length(g), "rows\n")

  suffixes <- unique(df$ISO3_suffix[g])
  cat(" Suffixes:", paste(suffixes, collapse =", "), "\n")

  cat("Years:", paste(unique(df$Year[g]), collapse=", "), "\n")
}
# ive added my varibles here not sure if thsi will affect it 
for (g in groups) {
  n <- length(g)
  lx <- as.numeric(df$lx[g])
  mx <- as.numeric(df$mx[g])
 
  
  dx <- matrix(NA, n-1)
  sx <- matrix(NA, n - 1)
  lxmx <- matrix(NA, n)
  lxmx_SUM <- matrix(NA, n)
  mx_ADJ <- matrix(NA, n)
  qx <- matrix(NA, n)
  vx <- matrix(NA, n)
  lxmx_raw <- matrix(NA, n)
  lxmx_STAND <- matrix(NA,n)
  lxmx_STAND_SUM_qx <- matrix(NA,n)
  vx_two <- matrix(NA,n)


  # dx and sx
  for (i in 1:(n-1)) {
    # dx = 1 - l(x + 1) / l(x)
    dx[i] <- 1 - lx[i+1] / lx[i]
    
    # sx = 1 - d(x)
    sx[i] <- 1 - dx[i]
  }
  df$dx[g] <- dx 
  df$sx[g] <- sx
  

#andy correction
lxmx_raw <- lx * mx
lxmx <- ifelse(is.na(lxmx_raw), 0, lxmx_raw) #checks through each and replaces NA with 0 avoid NA error
lxmx_SUM <- sum(lxmx)
lxmx_STAND <- lxmx / lxmx_SUM #lxmx standerdised
mx_ADJ <- lxmx_STAND /lx # mx adjusted by dividing the lxmx stnaderdised by normal lx 
#got rid of lxmx_ADJ as literally the same as lxmx_STAND (lxmx_ADJ = mx_ADJ * lx)
 
df$lxmx[g] <- lxmx
df$lxmx_STAND_SUM_qx[g] <- lxmx_STAND_SUM_qx
df$mx_ADj[g] <- mx_ADJ
df$lxmx_STAND[g] <- lxmx_STAND




for (i in 1:n) {
  lxmx_STAND_SUM_qx[i] <- sum(lxmx_STAND[i:n])
}

df$lxmx_STAND_SUM_qx[g]<- lxmx_STAND_SUM_qx

# vx
 for (i in 1:(n-1)) {
  vx[i] <- lxmx_STAND_SUM_qx[i+1]^2 / lx[i+1]^2
 }


 df$vx[g] <- vx
}


# write csv
write.csv(df, path, row.names = FALSE)