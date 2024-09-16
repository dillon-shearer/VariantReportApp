# VariantReportApp

## Project Overview

VariantReportApp is a GUI-based application built using PyQt5, designed to generate ALS WGS SNV reports from provided data files. The application integrates complex transformations, including case/control calculations, ethnicity handling, ClinVar, InterVar, and in silico predictions. The output is a comprehensive Excel report that includes multiple sheets, formulas, textboxes, and metadata/annotations such as ALSoD genes.

## Transformations

- **Case/Control Calculations:** The tool performs statistical calculations to compare case and control groups based on input data.
- **Ethnicity Handling:** Transformation logic includes handling ethnicities from provided metadata.
- **ClinVar and InterVar:** Variants are filtered based on ClinVar and InterVar significance scores.
- **In Silico Predictions:** The application evaluates damaging variant scores from in silico tools.

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

The application expects certain files to be in the following locations:
- `./data/ALS_genes.txt`: A list of ALS genes.
- `./data/ACMG_genes.txt`: A list of ACMG genes.
- `./data/AALS_937_exonic_report.txt.gz`: The exonic variant report.
- `./data/answer_metadata.csv`: Metadata for Answer ALS.
- `./data/alsod_genes.csv`: A file containing ALSoD genes.
- `./data/data_dictionary.txt`: A file containing the data dictionary for the generated reports.
- `./images/logo.png`: The logo for the application.

## Conclusion

VariantReportApp is designed to provide researchers with a streamlined tool for generating comprehensive SNV reports based on ALS WGS data, offering advanced filtering options and useful visualizations.
