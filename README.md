# NYC Motor Vehicle Collisions Analysis Project
##  Project Description
This project analyzes NYC Motor Vehicle Collision data to identify trends, high-risk areas, and factors contributing to accidents. The team worked to clean, integrate, and visualize data from NYC Open Data (Crashes and Persons datasets) using a Python-based pipeline and an interactive Dash web application.
###  Member 1:
The Data Engineering Lead focuses on the initial data pipeline, ensuring the core dataset is ready for integration and analysis.
**Core Tasks**
* **Data Loading:** Write and execute the Python code in the Jupyter/Colab notebook to load both the main Crashes dataset (`df_crashes`) and the Persons dataset (`df_persons`) directly from the NYC Open Data URLs using `pandas.read_csv`.
* **Exploratory Data Analysis (EDA):** Conduct a thorough initial exploration of `df_crashes`. This includes calculating descriptive statistics (e.g., `describe()`, `info()`), identifying the size, column types, and known issues like missing values and inconsistencies.
* **Pre-Integration Cleaning (Crashes):**
    * Handle missing values in critical columns like location (`BOROUGH`, `ZIP CODE`) and time (`CRASH DATE`, `CRASH TIME`). Provide written justifications in Markdown cells for choosing to drop rows or impute values.
    * Detect and address outliers in numerical columns like `NUMBER OF PERSONS INJURED/KILLED` using domain rules or statistical methods (e.g., IQR).
    * Standardize date/time formats and ensure categorical string columns (like `BOROUGH`) are consistent (e.g., upper case, no leading/trailing spaces).
    * Remove any duplicated records found in the `df_crashes` table.
* **Documentation:** Create detailed Markdown cells in the notebook documenting the steps 
###  Member 2:
This member is responsible for preparing the secondary data and ensuring a high-quality, fully integrated dataset.
**Core Tasks**
* **Secondary Data Cleaning:** Conduct EDA and perform pre-integration cleaning on the `df_persons` dataset. Focus on standardizing categorical data (e.g., `PERSON TYPE`, `INJURY TYPE`) and addressing missing values specific to this table.
* **Data Integration:** Use Python/Pandas to join the cleaned `df_crashes` and `df_persons` datasets using the common column `COLLISION_ID`. Document and justify the choice of join type (e.g., inner, left).
* **Post-Integration Cleaning:** This is a required step after the join. Resolve new issues created by the join:
    * New missing values resulting from the join (e.g., a person record without a crash record).
    * Inconsistent or redundant columns that appear in both original tables (e.g., if a similar time column exists in both).
    * Data type mismatches between the integrated fields.
* **Documentation:** Document the integration process, justify the data sources and join choices, and detail the post-integration cleaning steps in the notebook.
###  Member 3:
This member builds the foundation and user interface for the interactive website.
**Core Tasks**
* **Website Setup:** Select and set up the web framework (e.g., Dash/Plotly, React/Flask). Establish the basic layout and ensuring the layout is user-friendly and visually consistent.
* **Filtering Components:** Implement all required multiple dropdown filters on the website (e.g., Borough, Year, Vehicle Type, Contributing Factor, Injury Type).
* **Data Preparation for Web:** Write the necessary code to connect the cleaned, integrated dataset (from Member 2) to the website application.
* **Deployment:** Host the website using a free deployment platform (Vercel, Render, or Heroku) and confirm it is fully functional before submission.
###  Member 4: 
This member is responsible for generating dynamic insights and implementing the core interactivity of the report.
**Core Tasks**
* **Visualization Development:** Create a variety of charts (e.g., bar charts, line charts, heatmaps, maps, or pie charts) using Plotly (or Plotly.js) that address the team's research questions.
* **Chart Interactivity:** Ensure all visualizations offer required interactivity (hover, zoom, or filter updates).
* **Reporting Logic:** Implement the central "Generate Report" button. This button, when clicked, must dynamically process the selected filters (from Member 3 and 5) and update all visualizations simultaneously.
* **Code Quality:** Use clear code structure and modular functions for visualization generation. Add comments on complex plotting or data transformation logic.
###  Member 5:
This member handles the advanced website functionality, ensures all submission documentation is complete, and manages the team's version control.
**Core Tasks**
* **Search Mode Implementation:** Implement the advanced search mode functionality on the website. This allows users to type natural language queries (e.g., "Brooklyn 2022 pedestrian crashes") which the application must then parse to automatically apply the appropriate filters to the data..
* **GitHub Management:** Create and manage the GitHub repository for all project code, notebooks, and website files. Ensure all team members are added and have visible contributions (commits/pull requests).
* **README File:** Write the complete README file for the repository. This must include setup steps, deployment instructions, and a short, clear description of each team member's contribution to the milestone.
* **Notebook Review:** Review the Jupyter/Colab notebook to ensure it meets all grading criteria, including clean code, descriptive Markdown cells, and comprehensive visualization validation of the cleaning steps.
* **Code Review:** Review all code from both Notebook and website python file and make sure that all functions are working properly.
* **Render Hosting:** Host the website on Render and make sure that it runs correctly.
 Member 1:
Q1:
Which NYC borough has the highest crash rate per capita, and how does
this correlate with the number of fatalities and severe injuries?
Answer:
Raw Volume: Brooklyn consistently records the highest raw number of crashes (approx. 30-32% of total), followed closely by Queens.
Per Capita: When adjusted for residential population, Manhattan
often shows a higher "crash density" due to the influx of commuters and
tourists who do not live there but contribute to traffic.
Severity: While Manhattan has many fender-benders, Brooklyn and Queens
have higher fatality rates, often attributed to wider, faster arterial
roads (like Queens Boulevard or Atlantic Ave) compared to Manhattan's
gridlock.
Q2: Does the reported CONTRIBUTING FACTOR VEHICLE 1 vary significantly across different ZIP Codes?
Answer:
Dominant Factor: "Driver Inattention/Distraction" is the #1 contributing factor across nearly all ZIP codes, accounting for roughly 25-30% of all crashes.
Variations:
Dense Urban (Midtown Manhattan): Higher rates of "Failure to Yield Right-of-Way" and "Following Too Closely."
Outer Boroughs (Queens/Staten Island): Higher instances of "Unsafe Speed" and "Alcohol Involvement" appearing in the top 5, specifically in areas near highways.
 Member 2:
Q1: What is the distribution of injury severity across different Person Types?
Answer:
Drivers: Have the highest raw number of injuries but a relatively low fatality rate (K-Injury) due to vehicle safety features (airbags/seatbelts).
Pedestrians: Have the highest Severity Ratio.
A crash involving a pedestrian is significantly more likely to result
in a fatality or severe injury compared to a crash involving only
motorists.
Cyclists: Show a seasonal spike in injuries during warmer months, with severity often dependent on the presence of bike lanes.
Q2: Is there a correlation between Age Group, Safety Equipment, and injury outcomes?
Answer:
Safety Equipment:
There is a strong negative correlation between safety equipment use and
injury severity. Records with "None" or "Unknown" in the SAFETY_EQUIPMENT column show a drastically higher rate of Fatalities (K-Injury) compared to those listed as "Lap Belt/Harness" or "Helmet."
Age:
Young adults (18–25) are disproportionately involved in crashes due to
inexperience, while elderly pedestrians (65+) show the highest mortality
rate when involved in a crash due to physical frailty.
 Member 3:
Q1: What are the top three VEHICLE TYPE CODE categories involved in collisions?
Answer:
Sedan (Passenger Vehicle) - Consistently #1.
Station Wagon/SUV - Has been steadily rising and occasionally overtakes Sedans in recent years (2020–2024).
Taxi (or "Livery Vehicle" in older data) / Pick-up Truck - Taxis are prominent in Manhattan, while trucks appear more in outer boroughs.
Q2: Does the time of day influence the Contributing Factor?
Answer:
Morning/Evening Rush (6-10 AM, 4-7 PM): "Driver Inattention" and "Following Too Closely" peak here due to congestion.
Late Night (11 PM - 4 AM):
"Alcohol Involvement" and "Unsafe Speed" rise significantly as a
percentage of total crashes during these hours, despite lower traffic
volume.
Sunset: "Glare" appears as a statistically significant factor during specific hours depending on the season.
 Member 4:
Q1: What day of the week and time of day has the highest average number of incidents?
Answer:
Highest Risk Window: Friday afternoons between 4:00 PM and 6:00 PM consistently show the highest volume of crashes (The "Evening Rush" effect).
Lowest Risk Window: Monday mornings before 6:00 AM and Sundays before 10:00 AM typically show the lowest crash volumes.
Q2: Can a time series analysis identify trends or seasonality?
Answer:
Seasonality: Crashes generally peak in June/July (Summer travel) and October/November (Daylight Savings ending/darker evenings).
Lull: There is a consistent dip in crash numbers in January and February, likely due to snow/ice reducing the number of people driving or forcing slower speeds.
Long-term Trend:
Total crashes dropped massively in 2020 (COVID-19) and have been slowly
trending back up towards pre-pandemic levels in 2022-2024.
 Member 5:
Q1: How do bike collision rates differ between Manhattan and Queens?
Answer:
Manhattan: Has a higher density of bike crashes (crashes per square mile) due to the high volume of delivery cyclists and CitiBike usage.
Queens: While having fewer total bike crashes than Manhattan or Brooklyn, crashes in Queens often result in higher injury severity due to higher average vehicle speeds on wide roads lacking protected bike lanes.
Q2: Were there any specific short time periods with anomalously high/low crashes?
Answer:
Low Anomaly: March–April 2020 is the most significant anomaly in the dataset, where crash volume dropped by ~70% due to the COVID-19 lockdown.
High Anomalies: Specific dates often spike due to weather events (e.g., a sudden snowstorm causing a pile-up day) or holidays like New Year's Eve and Halloween, which see spikes in pedestrian/vehicle conflicts.

