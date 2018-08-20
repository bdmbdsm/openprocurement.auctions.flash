# -*- coding: utf-8 -*-
from openprocurement.auctions.core.tests.base import JSON_RENDERER_ERROR

from openprocurement.auctions.flash.tests.base import test_organization

# AuctionBidderResourceTest


def create_auction_bidder_invalid(self):
    response = self.app.post_json(
        '/auctions/some_id/bids',
        {
            'data': {
                'tenderers': [test_organization],
                "value": {
                    "amount": 500}}},
        status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])

    request_path = '/auctions/{}/bids'.format(self.auction_id)
    response = self.app.post(request_path, 'data', status=415)
    self.assertEqual(response.status, '415 Unsupported Media Type')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(
        response.json['errors'],
        [{u'description': u"Content-Type header should be one of "
                          u"['application/json']",
          u'location': u'header',
          u'name': u'Content-Type'}]
    )

    response = self.app.post(
        request_path, 'data', content_type='application/json', status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        JSON_RENDERER_ERROR
    ])

    response = self.app.post_json(request_path, 'data', status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Data not available',
            u'location': u'body', u'name': u'data'}
    ])

    response = self.app.post_json(
        request_path, {'not_data': {}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Data not available',
            u'location': u'body', u'name': u'data'}
    ])

    response = self.app.post_json(
        request_path, {
            'data': {
                'invalid_field': 'invalid_value'}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Rogue field', u'location':
            u'body', u'name': u'invalid_field'}
    ])

    response = self.app.post_json(
        request_path,
        {'data': {'tenderers': [{'identifier': 'invalid_value'}]}},
        status=422
    )
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(
        response.json['errors'],
        [{u'description': {
            u'identifier': [u'Please use a mapping for this field or '
                            u'Identifier instance instead of unicode.']},
          u'location': u'body',
          u'name': u'tenderers'}]
    )

    response = self.app.post_json(
        request_path,
        {'data': {'tenderers': [{'identifier': {}}]}},
        status=422
    )
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(
        response.json['errors'],
        [{u'description': [{u'contactPoint': [u'This field is required.'],
                            u'identifier': {
                            u'scheme': [u'This field is required.'],
                            u'id': [u'This field is required.']},
                            u'name': [u'This field is required.'],
                            u'address': [u'This field is required.']}],
          u'location': u'body',
          u'name': u'tenderers'}]
    )

    response = self.app.post_json(request_path, {'data': {'tenderers': [{
        'name': 'name', 'identifier': {'uri': 'invalid_value'}}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(
        response.json['errors'],
        [{u'description': [
             {u'contactPoint': [u'This field is required.'],
              u'identifier': {u'scheme': [u'This field is required.'],
                              u'id': [u'This field is required.'],
                              u'uri': [u'Not a well formed URL.']},
              u'address': [u'This field is required.']}
          ],
          u'location': u'body',
          u'name': u'tenderers'}]
     )

    response = self.app.post_json(
        request_path, {
            'data': {
                'tenderers': [test_organization]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(
        response.json['errors'],
        [{u'description': [u'This field is required.'],
          u'location': u'body',
          u'name': u'value'}]
    )

    response = self.app.post_json(
        request_path, {'data': {
            'tenderers': [test_organization], "value": {
                'amount': 500, 'valueAddedTaxIncluded': False
            }}}, status=422
    )
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(
        response.json['errors'],
        [{u'description': [
            u'valueAddedTaxIncluded of bid should be identical '
            u'to valueAddedTaxIncluded of value of auction'
        ],
            u'location': u'body', u'name': u'value'
        }]
    )

    response = self.app.post_json(
        request_path, {
            'data': {
                'tenderers': [test_organization], "value": {
                    "amount": 500, 'currency': "USD"}}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(
        response.json['errors'],
        [{u'description': [
            u'currency of bid should be identical to '
            u'currency of value of auction'
          ],
          u'location': u'body',
          u'name': u'value'}]
    )

    response = self.app.post_json(
        request_path, {
            'data': {
                'tenderers': test_organization, "value": {
                    "amount": 500}}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(
        response.json['errors'],
        [{u'description': u"invalid literal for int() with base 10: "
                          u"'contactPoint'",
          u'location': u'body',
          u'name': u'data'}]
    )


def create_auction_bidder(self):
    dateModified = self.db.get(self.auction_id).get('dateModified')
    response = self.app.post_json(
        '/auctions/{}/bids'.format(
            self.auction_id), {
            'data': {
                'tenderers': [test_organization], "value": {
                    "amount": 500}}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    bidder = response.json['data']
    self.assertEqual(bidder['tenderers'][0]['name'], test_organization['name'])
    self.assertIn('id', bidder)
    self.assertIn(bidder['id'], response.headers['Location'])

    self.assertEqual(
        self.db.get(
            self.auction_id).get('dateModified'),
        dateModified)

    self.set_status('complete')

    response = self.app.post_json(
        '/auctions/{}/bids'.format(
            self.auction_id), {
            'data': {
                'tenderers': [test_organization], "value": {
                    "amount": 500}}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(
        response.json['errors'][0]["description"],
        "Can't add bid in current (complete) auction status")


def patch_auction_bidder(self):
    response = self.app.post_json(
        '/auctions/{}/bids'.format(
            self.auction_id), {
            'data': {
                'tenderers': [test_organization], "status": "draft", "value": {
                    "amount": 500}}}
    )
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    bidder = response.json['data']
    bid_token = response.json['access']['token']
    response = self.app.patch_json(
        '/auctions/{}/bids/{}?acc_token={}'.format(
            self.auction_id, bidder['id'], bid_token
        ), {"data": {"value": {"amount": 60}}}, status=422
    )
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(
        response.json['errors'],
        [{
            u'description':
                [u'value of bid should be greater than value of auction'],
                u'location': u'body',
                u'name': u'value'
        }]
    )

    response = self.app.patch_json('/auctions/{}/bids/{}?acc_token={}'.format(
        self.auction_id, bidder['id'], bid_token
    ), {"data": {
        'tenderers': [
            {"name": u"Державне управління управлінням справами"}
        ]}}
    )
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['date'], bidder['date'])
    self.assertNotEqual(
        response.json['data']['tenderers'][0]['name'],
        bidder['tenderers'][0]['name'])

    response = self.app.patch_json('/auctions/{}/bids/{}?acc_token={}'.format(
        self.auction_id, bidder['id'], bid_token
    ), {"data": {"value": {"amount": 500}, 'tenderers': [test_organization]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['date'], bidder['date'])
    self.assertEqual(
        response.json['data']['tenderers'][0]['name'],
        bidder['tenderers'][0]['name'])

    response = self.app.patch_json('/auctions/{}/bids/{}?acc_token={}'.format(
        self.auction_id, bidder['id'], bid_token
    ), {"data": {"value": {"amount": 400}}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["value"]["amount"], 400)
    self.assertNotEqual(response.json['data']['date'], bidder['date'])

    response = self.app.patch_json('/auctions/{}/bids/{}?acc_token={}'.format(
        self.auction_id, bidder['id'], bid_token
    ), {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active")
    self.assertNotEqual(response.json['data']['date'], bidder['date'])

    response = self.app.patch_json('/auctions/{}/bids/{}?acc_token={}'.format(
        self.auction_id, bidder['id'], bid_token
    ), {"data": {"status": "draft"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(
        response.json['errors'][0]["description"],
        "Can\'t update bid to (draft) status")

    response = self.app.patch_json(
        '/auctions/{}/bids/some_id'.format(
            self.auction_id), {
            "data": {
                "value": {
                    "amount": 400}}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'bid_id'}
    ])

    response = self.app.patch_json(
        '/auctions/some_id/bids/some_id',
        {"data": {"value": {"amount": 400}}},
        status=404
    )
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])

    self.set_status('complete')

    response = self.app.get(
        '/auctions/{}/bids/{}'.format(self.auction_id, bidder['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["value"]["amount"], 400)

    response = self.app.patch_json('/auctions/{}/bids/{}?acc_token={}'.format(
        self.auction_id, bidder['id'], bid_token
    ), {"data": {"value": {"amount": 400}}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(
        response.json['errors'][0]["description"],
        "Can't update bid in current (complete) auction status")


def get_auction_bidder(self):
    response = self.app.post_json(
        '/auctions/{}/bids'.format(
            self.auction_id), {
            'data': {
                'tenderers': [test_organization], "value": {
                    "amount": 500}}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    bidder = response.json['data']
    bid_token = response.json['access']['token']

    response = self.app.get(
        '/auctions/{}/bids/{}'.format(
            self.auction_id, bidder['id']
        ), status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(
        response.json['errors'][0]["description"],
        "Can't view bid in current (active.tendering) auction status")

    response = self.app.get(
        '/auctions/{}/bids/{}?acc_token={}'.format(
            self.auction_id, bidder['id'], bid_token)
    )
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], bidder)

    self.set_status('active.qualification')

    response = self.app.get(
        '/auctions/{}/bids/{}'.format(self.auction_id, bidder['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    bidder_data = response.json['data']
    self.assertEqual(bidder_data, bidder)

    response = self.app.get(
        '/auctions/{}/bids/some_id'.format(self.auction_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'bid_id'}
    ])

    response = self.app.get('/auctions/some_id/bids/some_id', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])

    response = self.app.delete(
        '/auctions/{}/bids/{}?acc_token={}'.format(
            self.auction_id, bidder['id'], bid_token
        ), status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(
        response.json['errors'][0]["description"],
        "Can't delete bid in current (active.qualification) auction status"
    )


def delete_auction_bidder(self):
    response = self.app.post_json(
        '/auctions/{}/bids'.format(
            self.auction_id
        ), {'data': {
                'tenderers': [test_organization], "value": {
                    "amount": 500
                }
            }}
    )
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    bidder = response.json['data']
    bid_token = response.json['access']['token']

    response = self.app.delete(
        '/auctions/{}/bids/{}?acc_token={}'.format(
            self.auction_id, bidder['id'], bid_token
        )
    )
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], bidder)

    revisions = self.db.get(self.auction_id).get('revisions')
    self.assertTrue(any([i for i in revisions[-2][u'changes']
                         if i['op'] == u'remove' and i['path'] == u'/bids']))
    self.assertTrue(any([i for i in revisions[-1][u'changes']
                         if i['op'] == u'add' and i['path'] == u'/bids']))

    response = self.app.delete(
        '/auctions/{}/bids/some_id'.format(self.auction_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'bid_id'}
    ])

    response = self.app.delete('/auctions/some_id/bids/some_id', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])


def get_auction_auctioners(self):
    response = self.app.post_json(
        '/auctions/{}/bids'.format(
            self.auction_id), {
            'data': {
                'tenderers': [test_organization], "value": {
                    "amount": 500}}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    bidder = response.json['data']

    response = self.app.get(
        '/auctions/{}/bids'.format(self.auction_id), status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(
        response.json['errors'][0]["description"],
        "Can't view bids in current (active.tendering) auction status")

    self.set_status('active.qualification')

    response = self.app.get('/auctions/{}/bids'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'][0], bidder)

    response = self.app.get('/auctions/some_id/bids', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'auction_id'}
    ])


def bid_Administrator_change(self):
    response = self.app.post_json(
        '/auctions/{}/bids'.format(
            self.auction_id), {
            'data': {
                'tenderers': [test_organization], "value": {
                    "amount": 500}}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    bidder = response.json['data']

    self.app.authorization = ('Basic', ('administrator', ''))
    response = self.app.patch_json(
        '/auctions/{}/bids/{}'.format(
            self.auction_id, bidder['id']
        ), {"data": {
                'tenderers': [{"identifier": {"id": "00000000"}}],
                "value": {"amount": 400}}}
    )
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotEqual(response.json['data']["value"]["amount"], 400)
    self.assertEqual(
        response.json['data']["tenderers"][0]["identifier"]["id"],
        "00000000")

# AuctionBidderFeaturesResourceTest


def features_bidder(self):
    test_features_bids = [
        {
            "parameters": [
                {
                    "code": i["code"],
                    "value": 0.1,
                }
                for i in self.initial_data['features']
            ],
            "status": "active",
            "tenderers": [
                test_organization
            ],
            "value": {
                "amount": 469,
                "currency": "UAH",
                "valueAddedTaxIncluded": True
            }
        },
        {
            "parameters": [
                {
                    "code": i["code"],
                    "value": 0.15,
                }
                for i in self.initial_data['features']
            ],
            "tenderers": [
                test_organization
            ],
            "status": "draft",
            "value": {
                "amount": 479,
                "currency": "UAH",
                "valueAddedTaxIncluded": True
            }
        }
    ]
    for i in test_features_bids:
        response = self.app.post_json(
            '/auctions/{}/bids'.format(self.auction_id), {'data': i})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        bid = response.json['data']
        bid.pop(u'date')
        bid.pop(u'id')
        bid.pop(u'owner')
        self.assertEqual(bid, i)

# AuctionBidderDocumentResourceTest


def create_auction_bidder_document_nopending(self):
    response = self.app.post_json(
        '/auctions/{}/bids'.format(
            self.auction_id), {
            'data': {
                'tenderers': [test_organization], "value": {
                    "amount": 500}}})
    bid = response.json['data']
    bid_token = response.json['access']['token']
    bid_id = bid['id']

    response = self.app.post(
        '/auctions/{}/bids/{}/documents?acc_token={}'.format(
            self.auction_id, bid_id, bid_token
        ), upload_files=[('file', 'name.doc', 'content')]
    )
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])

    self.set_status('active.qualification')

    response = self.app.patch_json(
        '/auctions/{}/bids/{}/documents/{}?acc_token={}'.format(
            self.auction_id, bid_id, doc_id, bid_token
        ), {"data": {"description": "document description"}}, status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(
        response.json['errors'][0]["description"],
        "Can't update document because award of bid is not in pending state")

    response = self.app.put(
        '/auctions/{}/bids/{}/documents/{}?acc_token={}'.format(
            self.auction_id,
            bid_id,
            doc_id, bid_token
        ),
        'content3',
        content_type='application/msword',
        status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(
        response.json['errors'][0]["description"],
        "Can't update document because award of bid is not in pending state")

    response = self.app.post(
        '/auctions/{}/bids/{}/documents?acc_token={}'.format(
            self.auction_id, bid_id, bid_token
        ), upload_files=[('file', 'name.doc', 'content')], status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(
        response.json['errors'][0]["description"],
        "Can't add document because award of bid is not in pending state")
