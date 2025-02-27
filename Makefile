# ---------------------------------------------
# Part 1: Generate individual CSVs from XLSX files
# ---------------------------------------------

# Detect unique prefixes like Q3, Q4, etc.
SETS := $(shell ls Q*_*.xlsx 2>/dev/null | sed -E 's/(Q[0-9]+)_.*/\1/' | sort -u)

# List of all XLSX files
XLSX_FILES := $(wildcard Q*_*.xlsx)

# Generate corresponding CSV file names
CSV_FILES := $(XLSX_FILES:.xlsx=.csv)

# Rule: Process an XLSX file with clean.py to produce its CSV
%.csv: %.xlsx
	@echo "Processing $<..."
	python3 clean.py db.csv $<
	@echo "Generated $@"

# Default target: generate all CSV files
all: $(CSV_FILES)

# Target: process all XLSX files for a specific set (e.g., Q3)
$(SETS):
	@echo "Processing all XLSX files for $@..."
	$(MAKE) -s $(patsubst %.xlsx,%.csv,$(wildcard $@_*.xlsx))
	@echo "Finished processing $@"

# ---------------------------------------------
# Part 2: Clean targets
# ---------------------------------------------

# Clean all generated CSV files
clean:
	rm -f Q*_*.csv
	@echo "All generated CSV files removed."

# Clean CSV files for a specific set (e.g., make clean Q3)
clean_%:
	rm -f $*_*.csv
	@echo "Cleaned CSV files for $*."

# Mark phony targets
.PHONY: all $(SETS) clean clean_%

# ---------------------------------------------
# Part 3: Merge CSV files into final set files
# ---------------------------------------------

# Merge rule for a specific set (e.g., `make merge Q3`)
merge_%: $(wildcard $*_*.csv)
	@if [ -z "$(wildcard $*_*.csv)" ]; then \
	  echo "No CSV files found for $* to merge. Run 'make $*' first."; exit 1; \
	fi; \
	echo "Merging CSV files for $*..."; \
	python3 merge.py db.csv $*.csv $*.html $(wildcard $*_*.csv); \
	echo "Merge complete for $*."

.PHONY: merge
merge: 
	@if [ -z "$(SET)" ]; then \
	  echo "Usage: make merge_<set> (for example, make merge_Q3)"; exit 1; \
	fi;

