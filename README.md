# variant_reports.py
- **Created:** Nov 23, 2021
- **Modified:** Feb 3, 2022, May 13, 2024, September 15, 2024
- **Authors:**
  - Leandro Lima <leandro.lima@gladstone.ucsf.edu>
  - Stacia Wyman <staciawyman@berkeley.edu>
  - Dillon Shearer <dillon@onpointsci.com>

## Version

**Current version:** 2.0.0

## Overview

This script generates ALS WGS SNV reports by leveraging PyQt for an interactive GUI experience. It includes features such as:

- Selecting genes (ALS, ACMG, or custom)
- Choosing samples (AnswerALS)
- Filtering by synonymous SNVs, ethnicities, and upstream/downstream variants
- Multiple functionalities for generating variant reports and downloading them as Excel files.

## Dependencies

- Python 3.x
- pandas
- numpy
- PyQt5
- pytz
- logging

Install dependencies:

    pip install -r requirements.txt

## Features

- **Interactive GUI**: Built with PyQt5, the app allows users to select genes, samples, and variants through a graphical interface.
- **ALS and ACMG Gene Selections**: Offers pre-loaded ALS and ACMG gene lists with the ability to input custom genes.
- **Variant Filtering**: Provides options to filter out synonymous SNVs and include upstream/downstream variants.
- **Report Generation**: Compiles variant data into an Excel report with multiple sheets, including ClinVar, InterVar, and damaging variant data.

## Files Used

- ALS genes: `./data/ALS_genes.txt`
- ACMG genes: `./data/ACMG_genes.txt`
- Variant report: `./data/AALS_937_exonic_report.txt.gz`
- Metadata: `./data/answer_metadata.csv`
- ALSOD genes: `./data/alsod_genes.csv`
- Data dictionary: `./data/data_dictionary.txt`

## How to Use

1. Run the app:

    python variant_reports.py

2. Select options for genes, samples, and variants.
3. Generate the report by clicking on the "Create report" button.
4. View or save the generated Excel report with multiple sheets for detailed analysis.

## GUI Features

- **Help Menu**: Provides access to the About section and documentation.
- **Customizable Inputs**: Title inputs, gene selection, and sample selection can all be customized by the user.
- **Live Background**: The app supports a live background and styled UI with a purple theme.
