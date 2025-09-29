nbmerge $(ls chapter*/Chapter_?.ipynb 2>/dev/null | sort -V) -o pdf/CMSC320TextBook.ipynb
jupyter nbconvert --to pdf pdf/CMSC320TextBook.ipynb --output CMSC320TextBook.pdf

convert pdf/cover.png pdf/cover.pdf
