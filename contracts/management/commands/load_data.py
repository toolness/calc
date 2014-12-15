from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from contracts.models import Contract
import csv
import os
from datetime import datetime

class Command(BaseCommand):

    def handle(self, *args, **options):

        data_file = csv.reader(open(os.path.join(settings.BASE_DIR, 'contracts/docs/hourly_prices.csv'), 'r'))
        #skip header row
        next(data_file)
        
        for line in data_file:
            try:  
                if line[0]:
                    #create contract record, unique to vendor, labor cat
                    idv_piid = line[0]
                    vendor_name = line[7]
                    labor_category = line[8].strip().replace('\n', ' ')
                    
                    try:
                        contract = Contract.objects.get(idv_piid=idv_piid, labor_category=labor_category, vendor_name=vendor_name)
                    
                    except Contract.DoesNotExist:
                        contract = Contract()
                        contract.idv_piid = idv_piid
                        contract.labor_category = labor_category
                        contract.vendor_name = vendor_name

                    contract.education_level = contract.get_education_code(line[9])
                    contract.schedule = line[2]
                    contract.business_size = line[1]
                    contract.sin = line[6]

                    if line[4] != '':
                        contract.contract_start = datetime.strptime(line[4], '%m/%d/%Y').date()
                    if line[5] != '':
                        contract.contract_end = datetime.strptime(line[5], '%m/%d/%Y').date()
                
                    if line[10].strip() != '':
                        contract.min_years_experience = line[10]
                    else:
                        contract.min_years_experience = 0

                    if line[11] and line[11] != '': 
                        contract.hourly_rate_year1 = contract.normalize_rate(line[11])
                    else:
                        #there's no pricing info
                        continue
                    
                    for count, rate in enumerate(line[12:]):
                        if rate and rate.strip() != '':
                            setattr(contract, 'hourly_rate_year' + str(count+2), contract.normalize_rate(rate))
                    
                    
                    contract.contractor_site = line[3]

                    contract.save()
            except Exception as e:
                print(e)
                print(line)
                break
