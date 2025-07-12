import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.stats import linregress
import math

class QpcrApp:
    def __init__(self, master):
        self.master = master
        self.master.title("qPCR Calculator")
        self.slope = None       # Standard curve slope
        self.intercept = None   # Standard curve intercept
        self.r_value = None     # Regression r_value
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create frames for each tab
        self.standards_frame = ttk.Frame(self.notebook)
        self.samples_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.standards_frame, text="Standards")
        self.notebook.add(self.samples_frame, text="Samples")
        
        self.create_standards_tab()
        self.create_samples_tab()
    
    #########################
    # Standards Tab Methods #
    #########################
    def create_standards_tab(self):
        # Data entry frame for standards
        self.std_data_frame = ttk.Frame(self.standards_frame)
        self.std_data_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        # Headers for standard inputs
        ttk.Label(self.std_data_frame, text="Amount (e.g., ng, pg, uM, nM etc.)").grid(row=0, column=0, padx=5, pady=2)
        ttk.Label(self.std_data_frame, text="Average Cq").grid(row=0, column=1, padx=5, pady=2)
        
        # List to hold rows: each row is a tuple (amount_entry, cq_entry)
        self.std_rows = []
        for i in range(6):
            self.add_std_row()
        
        # Buttons for standards entry
        std_button_frame = ttk.Frame(self.std_data_frame)
        std_button_frame.grid(row=100, column=0, columnspan=2, pady=10)
        ttk.Button(std_button_frame, text="Add Row", command=self.add_std_row).pack(side=tk.LEFT, padx=5)
        ttk.Button(std_button_frame, text="Plot Standard Curve", command=self.plot_std_curve).pack(side=tk.LEFT, padx=5)
        
        # Matplotlib figure for the standard curve
        self.std_fig, self.std_ax = plt.subplots(figsize=(6, 4))
        self.std_ax.set_xlabel("log10(Amount)")
        self.std_ax.set_ylabel("Cq")
        self.std_ax.set_title("qPCR Standard Curve")
        self.std_ax.grid(True)
        self.std_canvas = FigureCanvasTkAgg(self.std_fig, master=self.standards_frame)
        self.std_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    def add_std_row(self):
        row_index = len(self.std_rows) + 1
        amount_entry = ttk.Entry(self.std_data_frame, width=15)
        cq_entry = ttk.Entry(self.std_data_frame, width=10)
        amount_entry.grid(row=row_index, column=0, padx=5, pady=2)
        cq_entry.grid(row=row_index, column=1, padx=5, pady=2)
        self.std_rows.append((amount_entry, cq_entry))
    
    def get_std_data(self):
        amounts = []
        cqs = []
        for i, (amount_entry, cq_entry) in enumerate(self.std_rows, start=1):
            amt_str = amount_entry.get().strip()
            cq_str = cq_entry.get().strip()
            if amt_str and cq_str:
                try:
                    amt = float(amt_str)
                    cq = float(cq_str)
                    amounts.append(amt)
                    cqs.append(cq)
                except ValueError:
                    messagebox.showerror("Invalid Input", f"Standard row {i} contains non-numeric data.")
                    return None, None
        if len(amounts) < 2:
            messagebox.showerror("Insufficient Data", "Please enter at least two standard data points.")
            return None, None
        return np.array(amounts), np.array(cqs)
    
    def plot_std_curve(self):
        amounts, cqs = self.get_std_data()
        if amounts is None or cqs is None:
            return
        
        log_amounts = np.log10(amounts)
        regression = linregress(log_amounts, cqs)
        self.slope = regression.slope
        self.intercept = regression.intercept
        self.r_value = regression.rvalue
        
        try:
            efficiency = (10 ** (-1 / self.slope) - 1) * 100
        except ZeroDivisionError:
            efficiency = float('nan')
        
        self.std_ax.clear()
        self.std_ax.grid(True)
        self.std_ax.set_xlabel("log10(Amount)")
        self.std_ax.set_ylabel("Cq")
        self.std_ax.set_title("qPCR Standard Curve")
        
        self.std_ax.scatter(log_amounts, cqs, color='blue', label="Data points")
        x_vals = np.linspace(min(log_amounts)-0.1, max(log_amounts)+0.1, 100)
        y_vals = self.slope * x_vals + self.intercept
        self.std_ax.plot(x_vals, y_vals, color='red', label="Fitted line")
        
        eq_text = f"Cq = {self.slope:.3f} * log10(Amount) + {self.intercept:.3f}"
        r2_text = f"R² = {self.r_value**2:.4f}"
        eff_text = f"PCR Efficiency = {efficiency:.2f}%"
        full_text = eq_text + "\n" + r2_text + "\n" + eff_text
        self.std_ax.text(0.05, 0.95, full_text, transform=self.std_ax.transAxes,
                         fontsize=10, verticalalignment='top',
                         bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))
        
        self.std_ax.legend()
        self.std_fig.tight_layout()
        self.std_canvas.draw()
    
    ########################
    # Samples Tab Methods  #
    ########################
    def create_samples_tab(self):
        # Instructions label
        instr = ("Enter sample data below. You can add a new sample (which includes the sample name) or add dilution rows to an existing sample.\n"
                 "For each dilution row, enter:\n"
                 " - Dilution Factor (e.g., for a 1:10 dilution, enter 10)\n"
                 " - Up to three Cq values (the average will be computed).\n"
                 "The app will calculate the undiluted amount for each dilution based on your standard curve\n"
                 "and then compute the average undiluted amount per sample.")
        ttk.Label(self.samples_frame, text=instr, justify=tk.LEFT).pack(padx=10, pady=5)
        
        # Create a frame for sample input that is scrollable.
        self.sample_input_frame = ttk.Frame(self.samples_frame)
        self.sample_input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create a canvas for scrolling sample sections.
        self.samples_canvas = tk.Canvas(self.sample_input_frame, height=300)
        self.samples_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Vertical scrollbar for the sample canvas.
        self.samples_scrollbar = ttk.Scrollbar(self.sample_input_frame, orient="vertical", command=self.samples_canvas.yview)
        self.samples_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.samples_canvas.configure(yscrollcommand=self.samples_scrollbar.set)
        
        # This container will hold all sample sections.
        self.samples_container = ttk.Frame(self.samples_canvas)
        self.samples_canvas.create_window((0, 0), window=self.samples_container, anchor="nw")
        self.samples_container.bind("<Configure>", lambda event: self.samples_canvas.configure(scrollregion=self.samples_canvas.bbox("all")))
        
        # Global buttons for samples (placed below the scrollable area)
        sample_button_frame = ttk.Frame(self.samples_frame)
        sample_button_frame.pack(padx=10, pady=5)
        ttk.Button(sample_button_frame, text="Add Sample", command=self.add_sample).pack(side=tk.LEFT, padx=5)
        ttk.Button(sample_button_frame, text="Calculate Samples", command=self.calculate_samples).pack(side=tk.LEFT, padx=5)
        ttk.Button(sample_button_frame, text="Show Average per Sample", command=self.show_sample_averages).pack(side=tk.LEFT, padx=5)
        
        # Results frame for averaged sample data and histogram; fixed size so it doesn't get squished.
        self.results_frame = ttk.Frame(self.samples_frame)
        self.results_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=5)
        
        # Text box for sample average results (table output).
        self.sample_avg_text = tk.Text(self.results_frame, height=6)
        self.sample_avg_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame for the histogram plot and log scale toggle.
        self.hist_frame = ttk.Frame(self.results_frame, height=300)
        self.hist_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=5)
        self.hist_frame.pack_propagate(False)  # Prevent frame from resizing to its contents.
        
        self.log_scale_var = tk.IntVar()
        log_toggle = ttk.Checkbutton(self.hist_frame, text="Logarithmic Y-Axis", variable=self.log_scale_var, command=self.update_histogram)
        log_toggle.pack(anchor=tk.W)
        
        # Create a matplotlib figure for the histogram.
        self.hist_fig, self.hist_ax = plt.subplots(figsize=(6, 4))
        self.hist_canvas = FigureCanvasTkAgg(self.hist_fig, master=self.hist_frame)
        self.hist_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # List to hold sample sections.
        self.samples = []
    
    def add_sample(self):
        """Adds a new sample section with its own sample name entry and an initial dilution row."""
        sample_frame = ttk.LabelFrame(self.samples_container, text="New Sample")
        sample_frame.pack(fill=tk.X, padx=5, pady=5, ipadx=5, ipady=5)
        
        # Sample name entry.
        ttk.Label(sample_frame, text="Sample Name:").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        name_entry = ttk.Entry(sample_frame, width=20)
        name_entry.grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
        
        # Frame for dilution rows (table header and rows).
        dilution_frame = ttk.Frame(sample_frame)
        dilution_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        headers = ["Dilution Factor", "Cq 1", "Cq 2", "Cq 3", "Avg Cq", "Undiluted Amount"]
        for col, header in enumerate(headers):
            ttk.Label(dilution_frame, text=header, borderwidth=1, relief="solid", width=15).grid(row=0, column=col, padx=1, pady=1)
        
        sample_dict = {"name_entry": name_entry, "dilution_rows": [], "frame": dilution_frame}
        self.samples.append(sample_dict)
        
        # Button to add dilution row for this sample.
        add_row_btn = ttk.Button(sample_frame, text="Add Dilution Row", command=lambda s=sample_dict: self.add_dilution_row(s))
        add_row_btn.grid(row=2, column=0, columnspan=2, pady=5)
        
        # Automatically add one dilution row initially.
        self.add_dilution_row(sample_dict)
    
    def add_dilution_row(self, sample_dict):
        """Adds a dilution row to the specified sample."""
        row_index = len(sample_dict["dilution_rows"]) + 1
        dilution_entry = ttk.Entry(sample_dict["frame"], width=15)
        cq1_entry = ttk.Entry(sample_dict["frame"], width=10)
        cq2_entry = ttk.Entry(sample_dict["frame"], width=10)
        cq3_entry = ttk.Entry(sample_dict["frame"], width=10)
        avg_cq_label = ttk.Label(sample_dict["frame"], text="N/A", width=15, relief="sunken")
        undiluted_label = ttk.Label(sample_dict["frame"], text="N/A", width=15, relief="sunken")
        
        dilution_entry.grid(row=row_index, column=0, padx=1, pady=1)
        cq1_entry.grid(row=row_index, column=1, padx=1, pady=1)
        cq2_entry.grid(row=row_index, column=2, padx=1, pady=1)
        cq3_entry.grid(row=row_index, column=3, padx=1, pady=1)
        avg_cq_label.grid(row=row_index, column=4, padx=1, pady=1)
        undiluted_label.grid(row=row_index, column=5, padx=1, pady=1)
        
        dilution_row = {
            "dilution_entry": dilution_entry,
            "cq1_entry": cq1_entry,
            "cq2_entry": cq2_entry,
            "cq3_entry": cq3_entry,
            "avg_cq_label": avg_cq_label,
            "undiluted_label": undiluted_label
        }
        sample_dict["dilution_rows"].append(dilution_row)
    
    def calculate_samples(self):
        # Ensure that a standard curve has been calculated.
        if self.slope is None or self.intercept is None:
            messagebox.showerror("No Standard Curve", "Please calculate the standard curve in the Standards tab first.")
            return
        
        for sample in self.samples:
            for dilution_row in sample["dilution_rows"]:
                dilution_str = dilution_row["dilution_entry"].get().strip()
                if not dilution_str:
                    messagebox.showerror("Missing Data", "Please enter a dilution factor for all dilution rows.")
                    return
                try:
                    dilution_factor = float(dilution_str)
                except ValueError:
                    messagebox.showerror("Invalid Input", "Dilution factor must be numeric.")
                    return
                
                # Get Cq values (ignore empty ones).
                cqs = []
                for key in ["cq1_entry", "cq2_entry", "cq3_entry"]:
                    val = dilution_row[key].get().strip()
                    if val:
                        try:
                            cqs.append(float(val))
                        except ValueError:
                            messagebox.showerror("Invalid Input", "Cq values must be numeric.")
                            return
                
                if not cqs:
                    dilution_row["avg_cq_label"].config(text="N/A")
                    dilution_row["undiluted_label"].config(text="N/A")
                    continue
                
                avg_cq = sum(cqs) / len(cqs)
                dilution_row["avg_cq_label"].config(text=f"{avg_cq:.3f}")
                
                # Use standard curve: Cq = slope * log10(amount) + intercept  => log10(amount) = (Cq - intercept) / self.slope.
                try:
                    log_amount = (avg_cq - self.intercept) / self.slope
                    amount_diluted = 10 ** log_amount
                except Exception:
                    amount_diluted = float('nan')
                
                undiluted_amount = amount_diluted * dilution_factor
                dilution_row["undiluted_label"].config(text=f"{undiluted_amount:.3e}")
    
    def show_sample_averages(self):
        """
        Computes the average undiluted amount for each sample, then displays a 
        tab-delimited table in the Text widget. This makes it easy to copy/paste into Excel.
        """
        # Group dilution rows by sample and compute average undiluted amount per sample.
        self.sample_avg_data = {}  # For the histogram
        # We'll build a list of lines in tab-delimited format.
        out_lines = ["Sample Name\tAverage Undiluted Amount\t# Dilutions"]
        
        for sample in self.samples:
            sample_name = sample["name_entry"].get().strip()
            if not sample_name:
                sample_name = "Unnamed Sample"
            values = []
            for dilution_row in sample["dilution_rows"]:
                undiluted_text = dilution_row["undiluted_label"].cget("text")
                try:
                    undiluted_value = float(undiluted_text)
                    values.append(undiluted_value)
                except ValueError:
                    continue
            if values:
                avg_val = sum(values) / len(values)
                self.sample_avg_data[sample_name] = avg_val
                # Append a tab-delimited line for this sample
                out_lines.append(f"{sample_name}\t{avg_val:.3e}\t{len(values)}")
        
        # Clear the text widget, then insert the table
        self.sample_avg_text.delete(1.0, tk.END)
        if len(out_lines) == 1:
            # Means no valid sample lines were appended
            self.sample_avg_text.insert(tk.END, "No sample results available.\n")
        else:
            self.sample_avg_text.insert(tk.END, "\n".join(out_lines))
        
        self.plot_histogram()
    
    def plot_histogram(self):
        """Plot a bar chart (histogram) of average undiluted amounts per sample."""
        self.hist_ax.clear()
        if not hasattr(self, "sample_avg_data") or not self.sample_avg_data:
            self.hist_ax.text(0.5, 0.5, "No sample data to plot", horizontalalignment="center")
            self.hist_canvas.draw()
            return
        
        sample_names = list(self.sample_avg_data.keys())
        avg_amounts = [self.sample_avg_data[name] for name in sample_names]
        x_pos = np.arange(len(sample_names))
        
        self.hist_ax.bar(x_pos, avg_amounts, align='center', alpha=0.7)
        self.hist_ax.set_xticks(x_pos)
        self.hist_ax.set_xticklabels(sample_names, rotation=45, ha='right')
        self.hist_ax.set_ylabel("Average Undiluted Amount")
        self.hist_ax.set_title("Sample Comparison")
        
        # Toggle y-axis scale based on the checkbutton.
        if self.log_scale_var.get():
            self.hist_ax.set_yscale("log")
        else:
            self.hist_ax.set_yscale("linear")
        
        # Prevent labels from being cut off
        self.hist_fig.tight_layout()
        self.hist_canvas.draw()
    
    def update_histogram(self):
        """Called when the log scale toggle changes."""
        self.plot_histogram()

if __name__ == '__main__':
    root = tk.Tk()
    app = QpcrApp(root)
    root.mainloop()