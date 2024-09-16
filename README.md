
# VariantReportApp

## Project Overview

VariantReportApp is a GUI-based application built using PyQt5, designed to generate ALS WGS SNV reports from provided data files. The application integrates complex transformations, including case/control calculations, ethnicity handling, ClinVar, InterVar, and in silico predictions. The output is a comprehensive Excel report that includes multiple sheets, formulas, textboxes, and metadata/annotations such as ALSoD genes.

## Transformations

- **Case/Control Calculations:** The tool performs statistical calculations to compare case and control groups based on input data.
- **Ethnicity Handling:** Transformation logic includes handling ethnicities from provided metadata.
- **ClinVar and InterVar:** Variants are filtered based on ClinVar and InterVar significance scores.
- **In Silico Predictions:** The application evaluates damaging variant scores from in silico tools.
- **C9orf72 and ATXN2 Filters:** Special filtering for C9orf72 and ATXN2 expansion samples.

## UI Overview

The application features a user-friendly graphical interface built with PyQt5. It includes several pages:
1. **Report Generation:** Users can input the report title, choose gene sets (ALS Genes, ACMG Genes, or custom), select sample types, and apply various filters like synonymous SNVs and ethnicity.
2. **Summary Page:** Displays the applied filters and summary statistics, such as total variants, total samples, and the number of genes. A pie chart visualizes the variant type distribution.

## Packages

- **PyQt5**: For building the GUI.
- **Pandas**: For data manipulation.
- **Numpy**: For numerical operations.
- **Matplotlib**: For generating visualizations.
- **XlsxWriter**: For exporting the report to Excel.

## Running the Application

To run the application:
1. Ensure all dependencies are installed by running:
    ```bash
    pip install PyQt5 pandas numpy matplotlib xlsxwriter
    ```
2. Run the `variant_reports.py` script using Python:
    ```bash
    python variant_reports.py
    ```

## Directory Structure

The application relies on a well-defined directory structure to ensure all necessary files are present. Below is the expected directory structure:

```
VariantReportApp/
│
├── data/
│   ├── ALS_genes.txt                    # List of ALS genes
│   ├── ACMG_genes.txt                   # List of ACMG genes
│   ├── AALS_937_exonic_report.txt.gz     # Exonic variant report
│   ├── answer_metadata.csv               # Metadata for Answer ALS
│   ├── alsod_genes.csv                   # ALSoD genes data
│   ├── data_dictionary.txt               # Data dictionary for generated reports
│
├── images/
│   ├── logo.png                          # Application logo
│   ├── spinner.gif                       # Loading spinner GIF
│   ├── background.jpeg                   # Background image
│
├── log/
│   ├── report_generation_YYYY-MM-DD_HHMM.log   # Generated logs for each report
│
├── reports/
│   ├── Example_Report_2024-09-16.xlsx    # Generated reports
│
└── variant_reports.py                    # Main Python script
```

## Files Description

1. **ALS_genes.txt**: A text file containing the list of ALS genes used in the report.
2. **ACMG_genes.txt**: A text file with ACMG gene listings, useful for comparison and selection.
3. **AALS_937_exonic_report.txt.gz**: The main compressed variant file to be processed.
4. **answer_metadata.csv**: Metadata file containing subject information, ancestry data, and more.
5. **alsod_genes.csv**: ALSoD genes data used in the report generation.
6. **data_dictionary.txt**: A text-based dictionary explaining the various columns and metrics used in the reports.
7. **logo.png**: The application's logo, displayed on the GUI.
8. **spinner.gif**: A loading spinner shown during report generation.
9. **background.jpeg**: Background image used in the application for aesthetic purposes.
10. **variant_reports.py**: The main Python script, containing the logic for the application.
11. **log/report_generation_*.log**: Log files generated during the report creation process.
12. **reports/**: Directory containing generated Excel reports.

## Conclusion

VariantReportApp is designed to provide researchers with a streamlined tool for generating comprehensive SNV reports based on ALS WGS data. It offers advanced filtering options and useful visualizations. The tool is designed for scalability and can be easily extended with additional features or data inputs.
