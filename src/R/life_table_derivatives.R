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

# coerce numeric fields
#df$Age <- as.numeric(df$Age)
#df$lx <- as.numeric(df$lx)
#df$mx <- as.numeric(df$mx)

# initialise
n <- nrow(df)
df$dx <- NA
df$sx <- NA
df$px <- NA
df$qx <- NA
df$vx <- NA

groups <- split(seq_len(n), paste(df$ISO3, df$Year), sep=":")

for (g in groups) {
  n <- length(g)
  lx <- df$lx[g]
  mx <- df$mx[g]
  
  dx <- matrix(NA, n-1)
  sx <- matrix(NA, n)
  px <- matrix(NA, n)
  qx <- matrix(NA, n)
  vx <- matrix(NA, n-1)
  
  # dx and sx
  for (i in 1:(n-1)) {
    # dx = 1 - l(x + 1) / l(x)
    dx[i] <- 1 - lx[i+1] / lx[i]
    
    # sx = 1 - d(x)
    sx[i] <- 1 - dx[i]
  }
  df$dx[g] <- dx 
  df$sx[g] <- sx
  
  # px (lxmx)
  for (i in 1:n) {
    # lxmx = lx * mx
    px[i] <- lx[i] * mx[i]
  }
  df$px[g] <- px
  
  # qx
  px[is.na(px)] <- 0 # treat NA as 0 for sum
  n = length(px)
  
  for (i in 1:n) {
    # qx = sum(px[x>n])
    qx[i] <- sum(px[i:n])
  }
  df$qx[g] <- qx
  
  # vx
  for (i in 1:(n-1)) {
    # vx = q(x + 1)^2 / l(x + 1)^2
    vx[i] <- qx[i+1]^2 / lx[i+1]^2
  }
  df$vx[g] <- vx
}

# write csv
write.csv(df, path, row.names = FALSE)