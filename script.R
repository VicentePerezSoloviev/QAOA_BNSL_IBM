
library(bnlearn, RJSONIO)
library(gtools)

nsamples = 5000
dataset_path = "cancer.rda"
csv_path = "cancer_5000_bic.csv"
score = "bic"
export_path = "cancer_5000_bic.txt"

file <- load(dataset_path)

df_arcs <- as.data.frame(arcs(bn))
write.csv(df_arcs , 'arcs_cancer.csv')

samples = rbn(bn, n = nsamples, debug = FALSE)
write.csv(samples, csv_path)
cols <- colnames(samples)

printer1<- file(export_path,"w")


for (x in cols) {
  cols <- colnames(samples)
  cols <- cols[! cols %in% c(x)]
  comb = combinations(length(cols), 2, v = cols, set = TRUE, repeats.allowed = FALSE)
  
  for (i in 1:(length(comb[,1]))){
    # both edges
    vars1 = c(comb[i, 1], x, comb[i, 2])
    e = empty.graph(colnames(samples))
    arc.set = matrix(c(c(comb[i, 1], x), c(comb[i, 2], x)), ncol = 2, byrow = TRUE, dimnames = list(NULL, c("from", "to")))
    arcs(e) = arc.set
    result1 = score(e, samples[colnames(samples)], type = score)
    
    writeLines(paste(x, comb[i, 1], comb[i, 2], result1), con=printer1,sep="\n")
    
    # 1 edge
    vars2 = c(comb[i, 1], x)
    e = empty.graph(colnames(samples))
    arc.set = matrix(c(comb[i, 1], x), ncol = 2, byrow = TRUE, dimnames = list(NULL, c("from", "to")))
    arcs(e) = arc.set
    plot(e)
    result2 = score(e, samples[colnames(samples)], type = score)
    
    writeLines(paste(x, comb[i, 1], result2), con=printer1,sep="\n")
    
    # 1 edge
    vars3 = c(x, comb[i, 2])
    e = empty.graph(colnames(samples))
    arc.set = matrix(c(comb[i, 2], x), ncol = 2, byrow = TRUE, dimnames = list(NULL, c("from", "to")))
    arcs(e) = arc.set
    result3 = score(e, samples[colnames(samples)], type = score)
    
    writeLines(paste(x, comb[i, 2], result3), con=printer1,sep="\n")
  }
  
  # 0 edge
  vars4 = c(x)
  e = empty.graph(colnames(samples))
  result4 = score(e, samples[colnames(samples)], type = score)
  
  writeLines(paste(x, result4), con=printer1,sep="\n")  
}


close(printer1)





