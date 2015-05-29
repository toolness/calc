from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from contracts.models import Contract
import csv
import os
import logging
from datetime import datetime, date

class Command(BaseCommand):

    def handle(self, *args, **options):
        log = logging.getLogger(__name__)

        log.info("Begin load_data task")

        log.info("Deleting existing contract records")
        Contract.objects.all().delete()

        data_file = csv.reader(open(os.path.join(settings.BASE_DIR, 'contracts/docs/hourly_prices.csv'), 'r'))
        
        #skip header row
        next(data_file)

        #used for removing expired contracts
        today = date.today()

        contracts = []

        log.info("Processing new datafile")
        for line in data_file:
            #replace annoying msft carraige return
            for num in range(0, len(line)):
                #also replace version with capital D
                line[num] = line[num].replace("_x000d_", "").replace("_x000D_", "")

            try:  
                if line[0]:
                    #create contract record, unique to vendor, labor cat
                    idv_piid = line[11]
                    vendor_name = line[10]
                    labor_category = line[0].strip().replace('\n', ' ')
                    
                    contract = Contract()
                    contract.idv_piid = idv_piid
                    contract.labor_category = labor_category
                    contract.vendor_name = vendor_name

                    contract.education_level = contract.get_education_code(line[6])
                    contract.schedule = line[12]
                    contract.business_size = line[8]
                    contract.contract_year = line[14]
                    contract.sin = line[13]

                    if line[15] != '':
                        contract.contract_start = datetime.strptime(line[15], '%m/%d/%Y').date()
                    if line[16] != '':
                        contract.contract_end = datetime.strptime(line[16], '%m/%d/%Y').date()
                
                    if line[7].strip() != '':
                        contract.min_years_experience = line[7]
                    else:
                        contract.min_years_experience = 0

                    if line[1] and line[1] != '': 
                        contract.hourly_rate_year1 = contract.normalize_rate(line[1])
                    else:
                        #there's no pricing info
                        continue
                    
                    for count, rate in enumerate(line[2:6]):
                        if rate and rate.strip() != '':
                            setattr(contract, 'hourly_rate_year' + str(count+2), contract.normalize_rate(rate))
                    
                    if contract.contract_end > today and contract.contract_start < today:
                        #it's a current contract, need to find which year we're in
                        start_day = contract.contract_start
                        for plus_year in range(0,5):
                            if date(year=start_day.year + plus_year, month=start_day.month, day=start_day.day) < today:
                                contract.current_price = getattr(contract, 'hourly_rate_year' + str(plus_year + 1))
                        
                    contract.contractor_site = line[9]
                    contracts.append(contract)

            except Exception as e:
                log.exception(e)
                log.warning(line)
                break

        log.info("Inserting records")
        Contract.objects.bulk_create(contracts)

        log.info("Updating search index")
        call_command('update_search_field', Contract._meta.app_label, Contract._meta.model_name)

        log.info("End load_data task")
