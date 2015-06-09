## Updating the contract data

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
- Year that the contract is in
- Contract begin date
- Contract end date

Save a copy of the CSV as the next version of the data in https://github.com/18F/calc/tree/master/contracts/docs. Overwrite `hourly_prices.csv` with the new file.

Run `./manage.py load_data`
