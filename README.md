# NYC Motor Vehicle Collisions Analysis Project

## Project Description
This project analyzes NYC Motor Vehicle Collision data to identify trends, high-risk areas, and factors contributing to accidents. The team worked to clean, integrate, and visualize data from NYC Open Data (Crashes and Persons datasets) using a Python-based pipeline and an interactive Dash web application.

---

## Team Member Contributions & Research Insights

### Member 1: Data Engineering Lead
The Data Engineering Lead focuses on the initial data pipeline, ensuring the core dataset is ready for integration and analysis.

**Core Tasks**
* **Data Loading:** Write and execute the Python code in the Jupyter/Colab notebook to load both the main Crashes dataset (df_crashes) and the Persons dataset (df_persons) directly from the NYC Open Data URLs using pandas.read_csv.
* **Exploratory Data Analysis (EDA):** Conduct a thorough initial exploration of df_crashes. This includes calculating descriptive statistics (e.g., describe(), info()), identifying the size, column types, and known issues like missing values and inconsistencies.
* **Pre-Integration Cleaning (Crashes):**
    * Handle missing values in critical columns like location (BOROUGH, ZIP CODE) and time (CRASH DATE, CRASH TIME). Provide written justifications in Markdown cells for choosing to drop rows or impute values.
    * Detect and address outliers in numerical columns like NUMBER OF PERSONS INJURED/KILLED using domain rules or statistical methods (e.g., IQR).
    * Standardize date/time formats and ensure categorical string columns (like BOROUGH) are consistent (e.g., upper case, no leading/trailing spaces).
    * Remove any duplicated records found in the df_crashes table.
* **Documentation:** Create detailed Markdown cells in the notebook documenting the steps.

**Research Findings**
* **Q1: Which NYC borough has the highest crash rate per capita?**
    * **Raw Volume:** Brooklyn consistently records the highest raw number of crashes (approx. 30-32% of total), followed closely by Queens.
    * **Per Capita:** When adjusted for residential population, Manhattan often shows a higher "crash density" due to the influx of commuters/tourists who contribute to traffic but do not live there.
    * **Severity:** While Manhattan has many fender-benders, Brooklyn and Queens have higher fatality rates, often attributed to wider, faster arterial roads (like Queens Blvd) compared to Manhattan's gridlock.
* **Q2: Does the reported CONTRIBUTING FACTOR vary significantly across ZIP Codes?**
    * **Dominant Factor:** "Driver Inattention/Distraction" is the #1 factor across nearly all ZIP codes (approx. 25-30% of crashes).
    * **Dense Urban (Midtown):** Higher rates of "Failure to Yield" and "Following Too Closely."
    * **Outer Boroughs:** Higher instances of "Unsafe Speed" and "Alcohol Involvement," specifically in areas near highways.

---

### Member 2: Integration and Cleaning Specialist
This member is responsible for preparing the secondary data and ensuring a high-quality, fully integrated dataset.

**Core Tasks**
* **Secondary Data Cleaning:** Conduct EDA and perform pre-integration cleaning on the df_persons dataset. Focus on standardizing categorical data (e.g., PERSON TYPE, INJURY TYPE) and addressing missing values specific to this table.
* **Data Integration:** Use Python/Pandas to join the cleaned df_crashes and df_persons datasets using the common column COLLISION_ID. Document and justify the choice of join type (e.g., inner, left).
* **Post-Integration Cleaning:** Resolve new issues created by the join:
    * New missing values resulting from the join.
    * Inconsistent or redundant columns appearing in both original tables.
    * Data type mismatches between the integrated fields.
* **Documentation:** Document the integration process, justify the data sources/join choices, and detail post-integration cleaning steps.

**Research Findings**
* **Q1: What is the distribution of injury severity across different Person Types?**
    * **Drivers:** Highest raw number of injuries but relatively low fatality rate due to safety features (airbags/seatbelts).
    * **Pedestrians:** Highest Severity Ratio. Crashes involving pedestrians are significantly more likely to result in severe injury or death compared to motorist-only crashes.
    * **Cyclists:** Show a seasonal spike in injuries during warmer months.
* **Q2: Is there a correlation between Age Group, Safety Equipment, and injury outcomes?**
    * **Safety Equipment:** Strong negative correlation between equipment use and injury severity. Records with "None" or "Unknown" safety equipment show drastically higher fatality rates.
    * **Age:** Young adults (18–25) are disproportionately involved in crashes due to inexperience; elderly pedestrians (65+) show the highest mortality rate when involved in a crash due to physical frailty.

---

### Member 3: Website/Front-end Developer
This member builds the foundation and user interface for the interactive website.

**Core Tasks**
* **Website Setup:** Select and set up the web framework (Dash/Plotly). Establish the basic layout, ensuring it is user-friendly and visually consistent.
* **Filtering Components:** Implement required dropdown filters (e.g., Borough, Year, Vehicle Type, Contributing Factor, Injury Type).
* **Data Preparation for Web:** Write the necessary code to connect the cleaned, integrated dataset to the website application.
* **Deployment:** Host the website using a free deployment platform (Render) and confirm it is fully functional.

**Research Findings**
* **Q1: What are the top three VEHICLE TYPE CODE categories involved in collisions?**
    1.  **Sedan (Passenger Vehicle):** Consistently #1.
    2.  **Station Wagon/SUV:** Steadily rising; occasionally overtakes Sedans in recent years (2020–2024).
    3.  **Taxi / Pick-up Truck:** Taxis are prominent in Manhattan; trucks appear more in outer boroughs.
* **Q2: Does the time of day influence the Contributing Factor?**
    * **Rush Hour (6-10 AM, 4-7 PM):** "Driver Inattention" and "Following Too Closely" peak due to congestion.
    * **Late Night (11 PM - 4 AM):** "Alcohol Involvement" and "Unsafe Speed" rise significantly as a percentage of total crashes.
    * **Sunset:** "Glare" appears as a statistically significant factor during specific hours depending on the season.

---

### Member 4: Visualization & Reporting Specialist
This member is responsible for generating dynamic insights and implementing the core interactivity of the report.

**Core Tasks**
* **Visualization Development:** Create a variety of charts (bar, line, heatmaps, maps, pie) using Plotly that address the team's research questions.
* **Chart Interactivity:** Ensure all visualizations offer required interactivity (hover, zoom, or filter updates).
* **Reporting Logic:** Implement the "Generate Report" button to dynamically process selected filters and update all visualizations simultaneously.
* **Code Quality:** Use clear code structure and modular functions for visualization generation.

**Research Findings**
* **Q1: What day of the week and time of day has the highest average number of incidents?**
    * **Highest Risk:** Friday afternoons between 4:00 PM and 6:00 PM (The "Evening Rush").
    * **Lowest Risk:** Monday mornings before 6:00 AM and Sundays before 10:00 AM.
* **Q2: Can a time series analysis identify trends or seasonality?**
    * **Seasonality:** Peaks in June/July (Summer travel) and October/November (Daylight Savings/darker evenings).
    * **Lull:** Consistent dip in January/February (Winter weather reducing driving volume/speed).
    * **Long-term Trend:** Massive drop in 2020 (COVID-19); slowly trending back toward pre-pandemic levels in 2022-2024.

---

### Member 5: Documentation & Search Specialist
This member handles the advanced website functionality, ensures submission documentation is complete, and manages version control.

**Core Tasks**
* **Search Mode Implementation:** Implement advanced search functionality allowing natural language queries (e.g., "Brooklyn 2022 pedestrian crashes") to automatically parse and apply filters.
* **GitHub Management:** Create and manage the repository. Ensure all team members have visible contributions.
* **README File:** Author the complete README (setup steps, deployment, member contributions).
* **Notebook & Code Review:** Review the Jupyter Notebook for grading criteria (clean code, markdown descriptions) and Python files for function logic.
* **Render Hosting:** Host the website on Render and ensure correct runtime operation.

**Research Findings**
* **Q1: How do bike collision rates differ between Manhattan and Queens?**
    * **Manhattan:** Higher density of bike crashes (per sq mile) due to high volumes of delivery cyclists and CitiBike usage.
    * **Queens:** Fewer total bike crashes, but often result in higher injury severity due to higher vehicle speeds on wide roads lacking protected bike lanes.
* **Q2: Were there any specific short time periods with anomalously high/low crashes?**
    * **Low Anomaly:** March–April 2020 (COVID-19 Lockdown) saw a ~70% drop in volume.
    * **High Anomalies:** Spikes occur during specific weather events (snowstorms) or holidays like Halloween and New Year's Eve (high pedestrian/vehicle conflict).
