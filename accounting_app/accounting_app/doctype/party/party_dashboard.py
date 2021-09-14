
from __future__ import unicode_literals

from frappe import _


def get_data():
	return {
		'fieldname': 'party',
		'transactions': [
			{
				'label': _('Sell'),
				'items': ['Sale Invoice']
			},
			{
				'label': _('Buy'),
				'items': ['Purchase Invoice']
			},
            {
                'label': 'Payments',
                'items': ['Payment Entry']
            }
		]
	}