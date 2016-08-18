import datetime

place = {'name': "Some random place", 'town': None, 'country': None,
             'postal_code': None, 'address_1': None, 'address_2': None}

# schedule data
dt_format = '%Y-%m-%d %H:%M:%S'

run_dt = {'start': (datetime.datetime.now()),
          'end': (datetime.datetime.now() + datetime.timedelta(days=1))}

schedule_dt = {'start': (datetime.datetime.now() + datetime.timedelta(days=5)),
               'end': (datetime.datetime.now() + datetime.timedelta(days=6))}

schedule_sales_dt = {'start': datetime.datetime.now(),
                     'end': schedule_dt.get('start')}


