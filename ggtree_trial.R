args <- commandArgs(trailingOnly = TRUE)

# Read arguments from the command line
metadata_file <- args[1]
newick_file <- args[2]
marker_column <- args[3]
highlight_column <- args[4]
highlights_list <- strsplit(args[5], ",")[[1]]

library(ggtree)
library(ggplot2)
library(ggtreeExtra)

tree <- read.tree(newick_file)
metadata <- read.table(metadata_file, sep = "\t", header = TRUE, stringsAsFactors = FALSE)

metadata$sample_id <- gsub(" ", "_", metadata$sequence)
label <- metadata$sample_id
marker_factor <- metadata[[marker_column]]

if (!marker_column %in% colnames(metadata)) {
  stop(paste("Column", marker_column, "not found in metadata."))
}

metadata_df <- data.frame(label = label, marker_column = marker_factor, stringsAsFactors = FALSE)

p <- ggtree(tree) %<+% metadata_df + 
  geom_tippoint(aes(color = marker_column), size = 2) +
  geom_tiplab(aes(label = label), size = 2, hjust = -0.3) +
  scale_color_brewer(palette = "Set1") +  
  theme(legend.position = "right") +
  labs(title = "Phylogenetic Tree with Metadata", color = marker_column)

for (highlight in highlights_list) {
  highlight_leaves <- grep(highlight, metadata[[highlight_column]])
  highlight_node <- MRCA(tree, highlight_leaves)
  p <- p + geom_highlight(node = highlight_node, fill = "red", alpha = 0.2)
}

ggsave("phylogenetic_tree_with_metadata.png", plot = p, width = 10, height = 8, dpi = 300)
