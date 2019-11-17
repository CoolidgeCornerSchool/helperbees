import json
import csv
json_file = 'orders.json'
with open(json_file) as f:
    data = json.load(f)
    orders = data['result']
with open('donations.tsv', 'w') as tsvfile:
    writer = csv.writer(tsvfile, delimiter='\t')
    for i in orders:
        offer = i['offer']
        amount = '${:,.2f}'.format(float(i['payment_gross']))
        writer.writerow([amount, offer['user_first_name'], offer['offer_type'], i['payment_date']])
