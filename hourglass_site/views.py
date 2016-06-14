from collections import OrderedDict
from django.shortcuts import render
import xlrd

from .forms import XlsForm, ProposedPriceListRow, ContractDetailsForm

def get_labor_categories(book):
    sheet = book.sheet_by_name('(3)Labor Categories')

    rownum = 3
    cats = []

    while True:
        sin = sheet.cell_value(rownum, 0)
        if not sin.strip():
            break

        cat = OrderedDict()
        cat['sin'] = sin
        cat['service'] = sheet.cell_value(rownum, 1)
        cat['min_education'] = sheet.cell_value(rownum, 2)
        cat['min_years_experience'] = sheet.cell_value(rownum, 3)
        cat['commercial_list_price'] = sheet.cell_value(rownum, 4)
        cat['unit_of_issue'] = sheet.cell_value(rownum, 5)
        cat['most_favored_customer'] = sheet.cell_value(rownum, 6)
        cat['best_discount'] = sheet.cell_value(rownum, 7)
        cat['mfc_price'] = sheet.cell_value(rownum, 8)
        cat['gsa_discount'] = sheet.cell_value(rownum, 9)
        cat['price_excluding_iff'] = sheet.cell_value(rownum, 10)
        cat['price_including_iff'] = sheet.cell_value(rownum, 11)
        cat['volume_discount'] = sheet.cell_value(rownum, 12)
        cats.append(cat)

        rownum += 1

    return cats

def import_xls_step_2(request, cats=None):
    rows = []

    if cats is None:
        form = ContractDetailsForm(
            request.POST,
            prefix='contract_details'
        )
        num_rows = int(request.POST['num_rows'])
        is_valid = True
        for i in range(num_rows):
            row = ProposedPriceListRow(
                request.POST,
                prefix='xls_row_%d' % i
            )
            rows.append(row)
            if not row.is_valid():
                is_valid = False
        if is_valid:
            raise NotImplementedError("TODO: Commit data to db")
    else:
        form = ContractDetailsForm(prefix='contract_details')
        for cat in cats:
            initial_data = dict(
                sin=cat['sin'],
                labor_category=cat['service'],
                education_level=cat['min_education'],
                min_years_experience=cat['min_years_experience'],
                current_price=cat['price_including_iff']
            )
            row = ProposedPriceListRow(
                initial=initial_data,
                prefix='xls_row_%d' % len(rows)
            )
            rows.append(row)

    return render(request, 'import_xls_step_2.html', {
        'form': form,
        'header_row': ProposedPriceListRow(),
        'rows': rows
    })

def import_xls(request):
    if request.method == 'POST':
        step = request.POST.get('step', '1')
        if step == '1':
            form = XlsForm(request.POST, request.FILES)
            if form.is_valid():
                f = request.FILES['xls']
                book = xlrd.open_workbook(file_contents=f.read())
                cats = get_labor_categories(book)
                return import_xls_step_2(request, cats)
        elif step == '2':
            return import_xls_step_2(request)
    else:
        form = XlsForm()

    return render(request, 'import_xls.html', {
        'form': form,
    })
