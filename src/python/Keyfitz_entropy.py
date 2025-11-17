import numpy as np
import pandas as pd
from src.python import log

def calculate_keyfitz_H(lx_values):
    """
    Calculate Keyfitz entropy using the fundamental matrix method (H_N).
    Following Giaimo (2024) Equation 2.
    
    Parameters:
    -----------
    lx_values : array-like
        Survivorship values from age 0 to maximum age (starting with lx[0] = 1.0)
    
    Returns:
    --------
    H : float
        Keyfitz entropy H_N
    """
    lx = np.array(lx_values, dtype=np.float64)
    
    # STEP 1: Remove age 0, start from age 1
    lx = lx[1:]
    omega = len(lx)
    
    if omega < 2:
        return np.nan
    
    # STEP 2: Calculate survival probabilities (vectorized - no loop!)
    # p[a] = lx[a+1] / lx[a], with safe division
    p = np.zeros(omega, dtype=np.float64)
    
    # Vectorized calculation for all ages at once
    with np.errstate(divide='ignore', invalid='ignore'):
        p[:-1] = np.where(lx[:-1] > 0, lx[1:] / lx[:-1], 0)
    p[-1] = 0  # Last age has p=0
    
    # STEP 3: Build transition matrix U (vectorized)
    # Instead of loop, use diagonal placement
    U = np.diag(p[:-1], k=-1)  # Subdiagonal in one line!
    
    # STEP 4: Calculate fundamental matrix N = (I - U)^-1
    I = np.eye(omega, dtype=np.float64)
    try:
        N = np.linalg.inv(I - U)
    except np.linalg.LinAlgError:
        return np.nan
    
    # STEP 5: Build mortality matrix M (vectorized)
    M = np.diag(1 - p)
    
    # STEP 6: Build vectors
    e = np.ones(omega, dtype=np.float64)
    e1 = np.zeros(omega, dtype=np.float64)
    e1[0] = 1
    
    # STEP 7: Calculate H_N using Giaimo (2024) formula
    # Chain matrix multiplications efficiently
    numerator = e @ N @ M @ N @ e1
    denominator = e @ N @ e1
    
    if denominator == 0:
        return np.nan
    
    return numerator / denominator


def calculate_H_for_dataset(life_table_df):
    """
    Calculate Keyfitz H for each (ISO3, ISO3_suffix, Year) in the life table.
    
    Parameters:
    -----------
    life_table_df : pd.DataFrame
        Life table with columns: ISO3, ISO3_suffix, Year, Age, lx
    
    Returns:
    --------
    H_df : pd.DataFrame
        DataFrame with columns: ISO3, ISO3_suffix, Year, H_N
    """
    # Handle NaN in ISO3_suffix
    life_table_df['ISO3_suffix'] = life_table_df['ISO3_suffix'].fillna('')
    
    # Group by country-year
    grouped = life_table_df.groupby(['ISO3', 'ISO3_suffix', 'Year'], dropna=False)
    total_groups = len(grouped)
    
    log.log(f"Processing {total_groups} country-year combinations...")
    
    # Pre-allocate results list with expected size (faster than appending)
    results = []
    
    # Progress tracking
    last_log = 0
    log_interval = max(1, total_groups // 20)  # Log ~20 times total
    
    for i, ((iso3, suffix, year), group) in enumerate(grouped):
        # Progress logging every 5%
        if i - last_log >= log_interval:
            percent = (i / total_groups) * 100
            log.log(f"Progress: {i}/{total_groups} ({percent:.1f}%)")
            last_log = i
        
        # Sort by age
        group = group.sort_values('Age')
        lx_values = group['lx'].values
        
        # Quick validation
        if len(lx_values) < 2:
            continue
        
        # Calculate H_N
        H_N = calculate_keyfitz_H(lx_values)
        
        # Only add successful calculations
        if not np.isnan(H_N):
            results.append({
                'ISO3': iso3,
                'ISO3_suffix': suffix if pd.notna(suffix) else '',
                'Year': year,
                'H_N': H_N
            })
    
    log.log(f"Completed! Successfully calculated H for {len(results)}/{total_groups} country-years")
    return pd.DataFrame(results)


def test_keyfitz_calculation():
    """
    Test the Keyfitz H calculation with simple examples.
    """
    log.log("Testing Keyfitz H calculation...")
    log.log("=" * 60)
    
    # Test 1: Constant mortality (exponential decay)
    ages = np.arange(0, 111)
    lx_constant = np.exp(-0.01 * ages)
    lx_constant = lx_constant / lx_constant[0]
    
    H_constant = calculate_keyfitz_H(lx_constant)
    log.log(f"\nTest 1: Constant mortality")
    log.log(f"  Keyfitz H_N: {H_constant:.4f}")
    log.log(f"  Expected: ≈ 1.0 (for constant mortality)")
    
    # Test 2: Increasing mortality (senescence)
    lx_senescence = np.exp(-0.0001 * ages**2)
    lx_senescence = lx_senescence / lx_senescence[0]
    
    H_senescence = calculate_keyfitz_H(lx_senescence)
    log.log(f"\nTest 2: Increasing mortality (senescence)")
    log.log(f"  Keyfitz H_N: {H_senescence:.4f}")
    log.log(f"  Expected: < 1.0 (mortality increases with age)")
    
    # Test 3: Decreasing mortality (negative senescence)
    lx_neg_senescence = np.ones(111)
    for i in range(1, 111):
        if i < 30:
            lx_neg_senescence[i] = lx_neg_senescence[i-1] * 0.999
        else:
            lx_neg_senescence[i] = lx_neg_senescence[i-1] * 0.99
    lx_neg_senescence = lx_neg_senescence / lx_neg_senescence[0]
    
    H_neg = calculate_keyfitz_H(lx_neg_senescence)
    log.log(f"\nTest 3: Decreasing then increasing mortality")
    log.log(f"  Keyfitz H_N: {H_neg:.4f}")
    log.log(f"  Expected: could be > or < 1.0 depending on pattern")
    
    log.log("\n" + "=" * 60)
    log.log("If these values look reasonable, the calculation is working!")
    
    return H_constant, H_senescence, H_neg


if __name__ == "__main__":
    test_keyfitz_calculation()