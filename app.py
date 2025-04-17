import PySimpleGUI as sg
import pandas as pd
from pathlib import Path
import subprocess
import os

def main():
    sg.theme("DarkBlue3")  # Modern theme
    font = ("Arial", 12)
    select_text_color = "#D3D3D3"  # White text color
    button_color = ("white", "#D3D3D3")  # White text on a darker gray background

    layout = [
        [sg.Text("Select Metadata File:", font=font, text_color=select_text_color), sg.Input(key="-METADATA-", enable_events=True), sg.FileBrowse(font=font, button_color=button_color)],
        [sg.Text("Select Newick File:", font=font, text_color=select_text_color), sg.Input(key="-NEWICK-", enable_events=True), sg.FileBrowse(font=font, button_color=button_color)],
        [sg.Text("Select Marker Column:", font=font, text_color=select_text_color), sg.Combo([], key="-MARKER_COLUMN-", size=(30, 1), readonly=True, font=font)],
        [sg.Text("Select Highlight Column:", font=font, text_color=select_text_color), sg.Combo([], key="-HIGHLIGHT_COLUMN-", size=(30, 1), readonly=True, enable_events=True, font=font)],
        [sg.Text("Select Values to Highlight:", font=font, text_color=select_text_color)],
        [sg.Listbox(values=[], key="-HIGHLIGHT_VALUES-", size=(40, 10), select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, font=font)],
        [sg.Button("Generate Plot", size=(15, 1), button_color=button_color, font=font), sg.Button("Exit", size=(10, 1), button_color=button_color, font=font)]
    ]

    # Create the window
    window = sg.Window("Phylogenetic Tree Plotter", layout)

    metadata_df = None

    while True:
        event, values = window.read()

        # Exit the application
        if event in (sg.WINDOW_CLOSED, "Exit"):
            break

        # Load metadata file and populate dropdowns
        if event == "-METADATA-":
            metadata_file = values["-METADATA-"]
            if Path(metadata_file).is_file():
                metadata_df = pd.read_csv(metadata_file, sep="\t")
                columns = metadata_df.columns.tolist()
                window["-MARKER_COLUMN-"].update(values=columns)
                window["-HIGHLIGHT_COLUMN-"].update(values=columns)

        # Populate highlight values when a highlight column is selected
        if event == "-HIGHLIGHT_COLUMN-" and metadata_df is not None:
            highlight_column = values["-HIGHLIGHT_COLUMN-"]
            if highlight_column in metadata_df.columns:
                unique_values = metadata_df[highlight_column].dropna().unique().tolist()
                window["-HIGHLIGHT_VALUES-"].update(values=unique_values)

        # Generate the plot
        if event == "Generate Plot":
            metadata_file = values["-METADATA-"]
            newick_file = values["-NEWICK-"]
            marker_column = values["-MARKER_COLUMN-"]
            highlight_column = values["-HIGHLIGHT_COLUMN-"]
            highlight_values = values["-HIGHLIGHT_VALUES-"]

            if not metadata_file or not newick_file or not marker_column or not highlight_column or not highlight_values:
                sg.popup_error("Please fill in all fields!")
                continue

            # Convert highlight values to a comma-separated string
            highlight_values_str = ",".join(highlight_values)

            # Call the R script using subprocess
            try:
                subprocess.run(
                    [
                        "Rscript",
                        "ggtree_trial.R",  # Path to your R script
                        metadata_file,
                        newick_file,
                        marker_column,
                        highlight_column,
                        highlight_values_str
                    ],
                    check=True
                )
                sg.popup("Plot generated successfully!")
                # Open the plot automatically
                plot_file = "phylogenetic_tree_with_metadata.png"  # Ensure this matches the output file in your R script
                if os.path.exists(plot_file):
                    subprocess.run(["xdg-open", plot_file])  # For Linux
                    # subprocess.run(["open", plot_file])  # For macOS
                    # subprocess.run(["start", plot_file], shell=True)  # For Windows
            except subprocess.CalledProcessError as e:
                sg.popup_error(f"Error generating plot: {e}")

    window.close()

if __name__ == "__main__":
    main()