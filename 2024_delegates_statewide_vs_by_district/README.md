# Democratic Delegate Allocation Scripts

These scripts parse data from The Green Papers to generate a table of 2024 Democratic primary delegate allocations under varying viability thresholds.

## Reproducibility Instructions

1.  **Dependencies:** Ensure you have Python 3 installed. You will need `beautifulsoup4` to parse the HTML data if you plan to re-scrape the pages.
    ```bash
    pip install beautifulsoup4
    ```

2.  **Provided Data:** The required data has been pre-parsed from the cached HTML pages of The Green Papers and is provided in the following JSON files:
    * `gp_results3.json`: Contains the statewide popular vote and overall delegate counts.
    * `cd_data.json`: Contains the exact district-level (CD) popular vote counts and CD delegate pool sizes for states that report them.
    * `actual_pledged.json`: Contains the actual real-world pledged delegate allocations from 2024 (with superdelegates explicitly deducted to ensure mathematical accuracy).

3.  **Run Parsing (Optional):** If you wish to re-extract the actual pledged delegates from the HTML pages yourself (requires the `htmls/` directory containing the downloaded state pages):
    ```bash
    python3 parse_actual_pledged.py
    ```

4.  **Generate Table:** The script `table_script.py` calculates the delegate distribution scenarios using Hamilton's method. It runs the mathematical simulation for the different viability thresholds (including separating At-Large and PLEO pools for the 5% Current Scheme simulation) and outputs a LaTeX table.
    ```bash
    python3 table_script.py
    ```

The final output is saved to `delegate_table.tex`.
