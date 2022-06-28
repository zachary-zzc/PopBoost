# process interpolate
# users should prepare:
# 1. map in raster format
# 2. ancient component qmatrix file from start k to end k
# 3. sample coordinate file

## example files
## 1. RasterMaps/tyc.asc
## 2. Qmatrix/tyc_K
## 3. tyc.coord

# run interpolate
# this will generate output files in current directory
Rscript interpolate.R RasterMaps/tyc.asc Qmatrix/tyc_K tyc.coord 2 5 output
