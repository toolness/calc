from collections import OrderedDict
from django.shortcuts import render
import xlrd

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

def import_xls(request):
    if request.method == 'POST':
        f = request.FILES['xls']
        book = xlrd.open_workbook(file_contents=f.read())
        cats = get_labor_categories(book)
    else:
        cats = None

    return render(request, 'import_excel.html', {
        'cats': cats
    })
