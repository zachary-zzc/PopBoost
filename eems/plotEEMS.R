## Check that the current directory contains the rEEMSplots source directory
if (file.exists("./rEEMSplots")) {
  install.packages("rEEMSplots", repos = NULL, type = "source")
} else {
  stop("Move to the directory that contains the rEEMSplots source to install the package.")
}

args <- commandArgs(T)
# 1 -- result directory
# 2 -- plot directory


## Possibly change the working directory with setwd()


## Part 2: Generate graphics
library(rEEMSplots)

mcmcpath = args[1]
plotpath = args[2]

eems.plots(mcmcpath, plotpath, longlat = TRUE)
