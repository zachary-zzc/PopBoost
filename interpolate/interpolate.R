source("POPSutilities.R")

colorGradientsList <- lColorGradients

args <- commandArgs(T)
# 1 -- asc raster file
# 2 -- ancient component prefix
# 3 -- sample coord file
# 3 -- start k
# 4 -- end k
# 5 -- output prefix

asc.raster <- args[1]
component_prefix <- args[2]
coord_file <- args[3]
startk <- as.int(args[4])
endk <- as.int(args[5])
output_prefix <- args[6]

grid <- createGridFromAsciiRaster(asc.raster)
constrains <- getConstraintsFromAsciiRaster(asc.raster)

coord <- read.table(coord_file)

for (k in startk:endk) {
  jpeg(paste0(output_prefix, "_", k, ".jpg"), width=640, height=480)
  qmat_file <- paste0(component_prefix, "_", k, ".qmat")
  qmat <- read.table(qmat_file)
  maps(matrix=qmat, coord, grid, constrains, method="max", main=paste0("Ancestry coefficients ", "(K=", k, ")"), xlab="Longitude", ylab="Latitude")
  dev.off()
}

for (k in startk:endk) {
  qmat_file <- paste0(component_prefix, "_", k, ".qmat")
  matrix <- read.table(qmat_file)
  K=ncol(matrix)
  KK = as.integer(K/2)
  listOutClusters=NULL
  matrixOfVectors =NULL
  pdf(paste0(output_prefix, "_", k, "_components", ".pdf"), width=12, height=4*(KK+1))
  par(mfrow = c(KK+1, 2))
  # for (j in 1:k) {
  #   clust=NULL
  #   clust= Krig(coord, matrix[,j], theta = 10)  
  #   look<- predict(clust,grid) # evaluate on a grid of points
  #   out<- as.surface( grid, look)
  #   listOutClusters[[j]] = out[[8]]	
  #   matrixOfVectors = cbind(matrixOfVectors,c(out[[8]]))	
  # }
  # long = out[[1]]
  # lat = out[[2]]
  # 
  # whichmax = matrix(apply(matrixOfVectors ,MARGIN=1,FUN=which.max),nrow=length(long))
  # 
  # for (j in 1:k) {
  #   ncolors=length(colorGradientsList[[j]])
  #   listOutClusters[[j]][ whichmax != j ] = NA
  #   image(long,lat,listOutClusters[[j]],col=colorGradientsList[[j]][(ncolors-9):ncolors],breaks=c(-200,.1,seq(.2,.9,.1),+200))
  #   points(coord,pch=19)
  # }
  for (j in 1:k) {
    clust=NULL
    clust= Krig(coord, matrix[,j], theta = 10)  
    look<- predict(clust,grid) # evaluate on a grid of points
    out<- as.surface( grid, look)
    ncolors=length(colorGradientsList[[j]])
    image(out,col=colorGradientsList[[j]][(ncolors-9):ncolors],breaks=c(-200,.1,seq(.2,.9,.1),+200))
    points(coord,pch=19)
  }
  dev.off()
}
