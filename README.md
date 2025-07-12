# qPCR Calculator

Interactive qPCR calculator for standard curve analysis, PCR efficiency estimation, and sample quantification using a Tkinter GUI.

## Features

- **Standard Curve Generator**
  - Enter known standard concentrations and average Cq values
  - Computes regression line: slope, intercept, R², and PCR efficiency
  - Plots curve with equation and annotations

- **Sample Quantification**
  - Add multiple samples and dilution rows
  - Enter up to three Cq values per dilution
  - Automatically computes average Cq and back-calculates undiluted amounts
  - Outputs a tabular summary of sample concentrations
  - Includes bar chart comparison with log scale toggle

- **Graphical Interface**
  - Built with Tkinter and embedded Matplotlib
  - Clean tab-based layout (Standards / Samples)

## Installation

```bash
git clone https://github.com/yourusername/qpcr-calculator.git
cd qpcr-calculator
pip install -r requirements.txt
```
### Dependencies 
- Python 3.7
- numpy
- matplotlib
- scipy
- tkinter

you can install missing packages with 
```bash
pip install numpy matplotlib scipy
```
## Usage
```bash
python qpcr_calculator.py
```
- Go to the Standards tab and input standard curve data.
- Click Plot Standard Curve to generate regression and efficiency.
- Go to the Samples tab to add unknowns, input dilutions and Cq values.
- Use Show Average per Sample to output a table and visualize comparisons.

## Author
Developed by Steven Ochoa as part of a broader research project on aptamer selection and molecular quantitation. 

