import datetime
import simplejson as json

STRIPE_FAKE_CARD_VISA = {'object': 'card',
                         'id': 'card_4242',
                         'exp_month': datetime.datetime.now().month,
                         'exp_year': datetime.datetime.now().year,
                         'number': '4242424242424242',
                         'cvc': 123
                         }

STRIPE_FAKE_CARD_MAST = {'object': 'card',
                         'id': 'card_4444',
                         'exp_month': datetime.datetime.now().month,
                         'exp_year': datetime.datetime.now().year,
                         'number': '5555555555554444',
                         'cvc': 123
                         }

STRIPE_FAKE_CUSTOMER = json.loads('{"account_balance": 0, "description": "luke", "default_source": "card_18UYUgEs5xQmEfl2ZAZmy3Ep", "subscriptions": {"has_more": false, "total_count": 0, "object": "list", "data": [], "url": "/v1/customers/cus_8m6iipOcTVbaFY/subscriptions"}, "object": "customer", "created": 1467882506, "currency": null, "email": null, "sources": {"has_more": false, "total_count": 1, "object": "list", "data": [{"dynamic_last4": null, "last4": "4242", "address_state": null, "address_zip_check": null, "address_country": null, "id": "card_18UYUgEs5xQmEfl2ZAZmy3Ep", "address_line2": null, "address_line1": null, "funding": "credit", "metadata": {}, "cvc_check": "pass", "exp_month": 7, "tokenization_method": null, "address_line1_check": null, "brand": "Visa", "object": "card", "fingerprint": "jowNVZxG8SeBNO9b", "exp_year": 2016, "address_zip": null, "customer": "cus_8m6iipOcTVbaFY", "address_city": null, "name": null, "country": "US"}], "url": "/v1/customers/cus_8m6iipOcTVbaFY/sources"}, "shipping": null, "livemode": false, "discount": null, "metadata": {}, "id": "cus_8m6iipOcTVbaFY", "delinquent": false}')

# Failed Cards
# expect card_declined
STRIPE_FAKE_CARD_DECLINED = {'object': 'card',
                         'id': 'card_0002',
                         'exp_month': datetime.datetime.now().month,
                         'exp_year': datetime.datetime.now().year,
                         'number': '4100000000000019',
                         'cvc': 123
                         }