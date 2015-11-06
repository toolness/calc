# CALC Data Imports

## About the data
https://github.com/18F/calc/tree/master/contracts/docs has all versions of the data that has been imported to date. https://github.com/18F/calc/blob/master/contracts/docs/hourly_prices.csv is the most recent data set.

The files that we get are in .xlsx format. They need to be converted to CSV. The columns should be arranged as such:
- Labor Category
- Year 1 or base rate
- Year 2 rate
- Year 3 rate
- Year 4 rate
- Year 5 rate
- Education level
- Minimum years of experience
- Business Size
- Location
- Company Name
- Contract number
- Schedule
- SIN number
- Current contract year
- Contract begin date
- Contract end date

##### Labor Category
Ex: "Mechanical Engineer". Cannot be empty.

##### Contract Year Rates 1-5
Ex: 253.88. The first year cannot be empty.

##### Education Level
Must be one of the following or empty:
- "High School"
- "Associates"
- "Bachelors"
- "Masters"
- "Ph.D"

##### Minimum Years of Experience
Must be an integer or empty.

##### Business Size
Must be one of the following or empty:
- "s" for small business
- "o" for other than small

##### Worksite Location
Must be one of the following or empty:
- "customer"
- "contractor"
- "both"

##### Company Name
Ex: "Great Products Inc." Must not be empty.

##### Contract ID
Ex: "GS-10F-0616P" Must not be empty.

##### Schedule Name
Must be one of the following or empty:
- AIMS
- Consolidated
- Environmental
- Logistics
- Language Services
- MOBIS
- PES

##### SIN Number
Ex: "235-34" or "235-34, 689-12".

##### Current Contract Year
Must be an integer from 1-5. Cannot be empty.

##### Contract Start Date and Contract End Date
Month/Day/Year Ex: "12/3/14"

## Schedule 70 data

Schedule 70 contracts have a slightly different data format and are imported through a separate process.

https://github.com/18F/calc/tree/master/contracts/docs/s70 has all versions of Schedule 70 data that have been imported to date.

https://github.com/18F/calc/blob/master/contracts/docs/s70/s70_data.csv is the most recent data.

The files that we get are also in .xlsx format. They need to be converted to CSV. It uses the same columns as above, but in a slightly different order:

- SIN number
- Labor Category
- Education level
- Minimum years of experience
- Unit of issue (currently ignored)
- Base rate
- Contract number
- Company Name
- Business size
- Schedule (always "IT Schedule 70")
- Location
- Current contract year
- Contract begin date
- Contract end date

## Updating the contract data

Save a copy of the CSV as the next version of the data in https://github.com/18F/calc/tree/master/contracts/docs. Overwrite `hourly_prices.csv` with the new file.

Run `./manage.py load_data`

This will replace all existing records with the ones in the CSV.

Save a copy of the Schedule 70 CSV as the next version of the data in https://github.com/18F/calc/tree/master/contracts/s70/docs. Overwrite `s70_data.csv` with the new file.

Run `./manage.py load_s70`

This will replace all existing Schedule 70 records with the ones in the CSV.

For more information on the Schedule 70 data loader and its configuration options, run `./manage.py load_s70 --help`

Should the format of the file we import ever change, run `./manage.py makemigrations` and alert the team that they will need to run migrations on their local environments. 

## Updating data on Cloud Foundry
Before pushing to an app, edit the `manifest.yml` and under the environment you want to push to, add `command: bash cf.sh`.
