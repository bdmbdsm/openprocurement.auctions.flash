# -*- coding: utf-8 -*-
from email.header import Header

# AuctionDocumentResourceTest


def create_auction_document(self):
    response = self.app.get('/auctions/{}/documents'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json, {"data": []})

    response = self.app.post('/auctions/{}/documents?acc_token={}'.format(
        self.auction_id, self.auction_token
    ), upload_files=[('file', u'укр.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])
    self.assertEqual(u'укр.doc', response.json["data"]["title"])
    if self.docservice:
        self.assertIn('Signature=', response.json["data"]["url"])
        self.assertIn('KeyID=', response.json["data"]["url"])
        self.assertNotIn('Expires=', response.json["data"]["url"])
        key = response.json["data"]["url"].split('/')[-1].split('?')[0]
        auction = self.db.get(self.auction_id)
        self.assertIn(key, auction['documents'][-1]["url"])
        self.assertIn('Signature=', auction['documents'][-1]["url"])
        self.assertIn('KeyID=', auction['documents'][-1]["url"])
        self.assertNotIn('Expires=', auction['documents'][-1]["url"])
    else:
        key = response.json["data"]["url"].split('?')[-1].split('=')[-1]

    response = self.app.get('/auctions/{}/documents'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual(u'укр.doc', response.json["data"][0]["title"])

    response = self.app.get('/auctions/{}/documents/{}?download=some_id'.format(
        self.auction_id, doc_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
    ])

    if self.docservice:
        response = self.app.get('/auctions/{}/documents/{}?download={}'.format(
            self.auction_id, doc_id, key))
        self.assertEqual(response.status, '302 Moved Temporarily')
        self.assertIn('http://localhost/get/', response.location)
        self.assertIn('Signature=', response.location)
        self.assertIn('KeyID=', response.location)
        self.assertNotIn('Expires=', response.location)
    else:
        response = self.app.get('/auctions/{}/documents/{}?download=some_id'.format(
            self.auction_id, doc_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
        ])

        response = self.app.get('/auctions/{}/documents/{}?download={}'.format(
            self.auction_id, doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 7)
        self.assertEqual(response.body, 'content')

    response = self.app.get('/auctions/{}/documents/{}'.format(
        self.auction_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual(u'укр.doc', response.json["data"]["title"])

    response = self.app.post(
        '/auctions/{}/documents?acc_token={}'.format(
            self.auction_id, self.auction_token
        ), upload_files=[('file', u'укр.doc'.encode(
            "ascii", "xmlcharrefreplace"
        ), 'content')]
    )
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(u'укр.doc', response.json["data"]["title"])
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])
    self.assertNotIn('acc_token', response.headers['Location'])

    self.set_status('active.tendering')

    response = self.app.post(
        '/auctions/{}/documents?acc_token={}'.format(
            self.auction_id, self.auction_token
        ), upload_files=[('file', u'укр.doc', 'content')], status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(
        response.json['errors'][0]["description"],
        "Can't add document in current (active.tendering) auction status")


def put_auction_document(self):
    from six import BytesIO
    from urllib import quote
    body = u'''--BOUNDARY\nContent-Disposition: form-data; name="file"; filename={}\nContent-Type: application/msword\n\ncontent\n'''.format(  # noqa: E501
        u'\uff07')
    environ = self.app._make_environ()
    environ['CONTENT_TYPE'] = 'multipart/form-data; boundary=BOUNDARY'
    environ['REQUEST_METHOD'] = 'POST'
    req = self.app.RequestClass.blank(self.app._remove_fragment(
        '/auctions/{}/documents'.format(self.auction_id)), environ)
    req.environ['wsgi.input'] = BytesIO(body.encode('utf8'))
    req.content_length = len(body)
    response = self.app.do_request(req, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(
        response.json['errors'][0]["description"],
        "could not decode params")

    body = u'''--BOUNDARY\nContent-Disposition: form-data; name="file"; filename*=utf-8''{}\nContent-Type: application/msword\n\ncontent\n'''.format(  # noqa: E501
        quote('укр.doc'))
    environ = self.app._make_environ()
    environ['CONTENT_TYPE'] = 'multipart/form-data; boundary=BOUNDARY'
    environ['REQUEST_METHOD'] = 'POST'
    req = self.app.RequestClass.blank(self.app._remove_fragment(
        '/auctions/{}/documents?acc_token={}'.format(self.auction_id, self.auction_token)
    ), environ)
    req.environ['wsgi.input'] = BytesIO(body.encode(req.charset or 'utf8'))
    req.content_length = len(body)
    response = self.app.do_request(req)
    # response = self.app.post('/auctions/{}/documents'.format(
    # self.auction_id), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(u'укр.doc', response.json["data"]["title"])
    doc_id = response.json["data"]['id']
    dateModified = response.json["data"]['dateModified']
    datePublished = response.json["data"]['datePublished']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.put(
        '/auctions/{}/documents/{}?acc_token={}'.format(
            self.auction_id, doc_id, self.auction_token
        ), upload_files=[('file', 'name  name.doc', 'content2')]
    )
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    if self.docservice:
        self.assertIn('Signature=', response.json["data"]["url"])
        self.assertIn('KeyID=', response.json["data"]["url"])
        self.assertNotIn('Expires=', response.json["data"]["url"])
        key = response.json["data"]["url"].split('/')[-1].split('?')[0]
        auction = self.db.get(self.auction_id)
        self.assertIn(key, auction['documents'][-1]["url"])
        self.assertIn('Signature=', auction['documents'][-1]["url"])
        self.assertIn('KeyID=', auction['documents'][-1]["url"])
        self.assertNotIn('Expires=', auction['documents'][-1]["url"])
    else:
        key = response.json["data"]["url"].split('?')[-1].split('=')[-1]

    if self.docservice:
        response = self.app.get('/auctions/{}/documents/{}?download={}'.format(
            self.auction_id, doc_id, key))
        self.assertEqual(response.status, '302 Moved Temporarily')
        self.assertIn('http://localhost/get/', response.location)
        self.assertIn('Signature=', response.location)
        self.assertIn('KeyID=', response.location)
        self.assertNotIn('Expires=', response.location)
    else:
        response = self.app.get('/auctions/{}/documents/{}?download={}'.format(
            self.auction_id, doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, 'content2')

    response = self.app.get('/auctions/{}/documents/{}'.format(
        self.auction_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('name name.doc', response.json["data"]["title"])
    dateModified2 = response.json["data"]['dateModified']
    self.assertTrue(dateModified < dateModified2)
    self.assertEqual(
        dateModified,
        response.json["data"]["previousVersions"][0]['dateModified'])
    self.assertEqual(response.json["data"]['datePublished'], datePublished)

    response = self.app.get(
        '/auctions/{}/documents?all=true'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(dateModified, response.json["data"][0]['dateModified'])
    self.assertEqual(dateModified2, response.json["data"][1]['dateModified'])

    response = self.app.post('/auctions/{}/documents?acc_token={}'.format(
        self.auction_id, self.auction_token
    ), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    dateModified = response.json["data"]['dateModified']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.get('/auctions/{}/documents'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(dateModified2, response.json["data"][0]['dateModified'])
    self.assertEqual(dateModified, response.json["data"][1]['dateModified'])

    response = self.app.put(
        '/auctions/{}/documents/{}?acc_token={}'.format(
            self.auction_id, doc_id, self.auction_token
        ), status=404, upload_files=[('invalid_name', 'name.doc', 'content')]
    )
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'body', u'name': u'file'}
    ])

    response = self.app.put(
        '/auctions/{}/documents/{}?acc_token={}'.format(
            self.auction_id,
            doc_id, self.auction_token
        ), 'content3', content_type='application/msword'
    )
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    if self.docservice:
        self.assertIn('Signature=', response.json["data"]["url"])
        self.assertIn('KeyID=', response.json["data"]["url"])
        self.assertNotIn('Expires=', response.json["data"]["url"])
        key = response.json["data"]["url"].split('/')[-1].split('?')[0]
        auction = self.db.get(self.auction_id)
        self.assertIn(key, auction['documents'][-1]["url"])
        self.assertIn('Signature=', auction['documents'][-1]["url"])
        self.assertIn('KeyID=', auction['documents'][-1]["url"])
        self.assertNotIn('Expires=', auction['documents'][-1]["url"])
    else:
        key = response.json["data"]["url"].split('?')[-1].split('=')[-1]

    if self.docservice:
        response = self.app.get('/auctions/{}/documents/{}?download={}'.format(
            self.auction_id, doc_id, key))
        self.assertEqual(response.status, '302 Moved Temporarily')
        self.assertIn('http://localhost/get/', response.location)
        self.assertIn('Signature=', response.location)
        self.assertIn('KeyID=', response.location)
        self.assertNotIn('Expires=', response.location)
    else:
        response = self.app.get('/auctions/{}/documents/{}?download={}'.format(
            self.auction_id, doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, 'content3')

    self.set_status('active.tendering')

    response = self.app.put(
        '/auctions/{}/documents/{}?acc_token={}'.format(
            self.auction_id, doc_id, self.auction_token
        ), upload_files=[('file', 'name.doc', 'content3')], status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(
        response.json['errors'][0]["description"],
        "Can't update document in current (active.tendering) auction status"
    )


def patch_auction_document(self):
    response = self.app.post('/auctions/{}/documents?acc_token={}'.format(
        self.auction_id, self.auction_token
    ), upload_files=[('file', str(Header(u'укр.doc', 'utf-8')), 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])
    self.assertEqual(u'укр.doc', response.json["data"]["title"])
    self.assertNotIn("documentType", response.json["data"])

    response = self.app.patch_json(
        '/auctions/{}/documents/{}?acc_token={}'.format(
            self.auction_id, doc_id, self.auction_token
        ), {"data": {"documentOf": "lot"}}, status=422
    )
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [{u'description': [
                     u'This field is required.'], u'location': u'body', u'name': u'relatedItem'}, ])

    response = self.app.patch_json(
        '/auctions/{}/documents/{}?acc_token={}'.format(
            self.auction_id, doc_id, self.auction_token
        ), {"data": {"documentOf": "lot", "relatedItem": '0' * 32}}, status=422
    )
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [{u'description': [
                     u'relatedItem should be one of lots'], u'location': u'body', u'name': u'relatedItem'}])

    response = self.app.patch_json(
        '/auctions/{}/documents/{}?acc_token={}'.format(
            self.auction_id, doc_id, self.auction_token
        ), {"data": {"documentOf": "item", "relatedItem": '0' * 32}}, status=422
    )
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [{u'description': [
                     u'relatedItem should be one of items'], u'location': u'body', u'name': u'relatedItem'}])

    response = self.app.patch_json(
        '/auctions/{}/documents/{}?acc_token={}'.format(
            self.auction_id, doc_id, self.auction_token
        ), {"data": {"description": "document description",
                     "documentType": 'auctionNotice'}}
    )
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertIn("documentType", response.json["data"])
    self.assertEqual(response.json["data"]["documentType"], 'auctionNotice')

    response = self.app.patch_json(
        '/auctions/{}/documents/{}?acc_token={}'.format(
            self.auction_id, doc_id, self.auction_token
        ), {"data": {"documentType": None}}
    )
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertNotIn("documentType", response.json["data"])

    response = self.app.get(
        '/auctions/{}/documents/{}'.format(self.auction_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual(
        'document description',
        response.json["data"]["description"])

    self.set_status('active.tendering')

    response = self.app.patch_json(
        '/auctions/{}/documents/{}?acc_token={}'.format(
            self.auction_id, doc_id, self.auction_token
        ), {"data": {"description": "document description"}}, status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(
        response.json['errors'][0]["description"],
        "Can't update document in current (active.tendering) auction status"
    )

# AuctionDocumentWithDSResourceTest


def create_auction_document_json(self):
    response = self.app.post_json('/auctions/{}/documents?acc_token={}'.format(
        self.auction_id, self.auction_token
    ),
                                  {'data': {
                                      'title': u'укр.doc',
                                      'url': self.generate_docservice_url(),
                                      'hash': 'md5:' + '0' * 32,
                                      'format': 'application/msword',
                                  }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])
    self.assertEqual(u'укр.doc', response.json["data"]["title"])
    self.assertIn('Signature=', response.json["data"]["url"])
    self.assertIn('KeyID=', response.json["data"]["url"])
    self.assertNotIn('Expires=', response.json["data"]["url"])
    key = response.json["data"]["url"].split('/')[-1].split('?')[0]
    auction = self.db.get(self.auction_id)
    self.assertIn(key, auction['documents'][-1]["url"])
    self.assertIn('Signature=', auction['documents'][-1]["url"])
    self.assertIn('KeyID=', auction['documents'][-1]["url"])
    self.assertNotIn('Expires=', auction['documents'][-1]["url"])

    response = self.app.get('/auctions/{}/documents'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual(u'укр.doc', response.json["data"][0]["title"])

    response = self.app.get('/auctions/{}/documents/{}?download=some_id'.format(
        self.auction_id, doc_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
    ])

    response = self.app.get('/auctions/{}/documents/{}?download={}'.format(
        self.auction_id, doc_id, key))
    self.assertEqual(response.status, '302 Moved Temporarily')
    self.assertIn('http://localhost/get/', response.location)
    self.assertIn('Signature=', response.location)
    self.assertIn('KeyID=', response.location)
    self.assertNotIn('Expires=', response.location)

    response = self.app.get('/auctions/{}/documents/{}'.format(
        self.auction_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual(u'укр.doc', response.json["data"]["title"])

    self.set_status('active.tendering')

    response = self.app.post_json('/auctions/{}/documents?acc_token={}'.format(
        self.auction_id, self.auction_token
    ),
                                  {'data': {
                                      'title': u'укр.doc',
                                      'url': self.generate_docservice_url(),
                                      'hash': 'md5:' + '0' * 32,
                                      'format': 'application/msword',
                                  }}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(
        response.json['errors'][0]["description"],
        "Can't add document in current (active.tendering) auction status")


def put_auction_document_json(self):
    response = self.app.post_json('/auctions/{}/documents?acc_token={}'.format(
        self.auction_id, self.auction_token
    ),
                                  {'data': {
                                      'title': u'укр.doc',
                                      'url': self.generate_docservice_url(),
                                      'hash': 'md5:' + '0' * 32,
                                      'format': 'application/msword',
                                  }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(u'укр.doc', response.json["data"]["title"])
    doc_id = response.json["data"]['id']
    dateModified = response.json["data"]['dateModified']
    datePublished = response.json["data"]['datePublished']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.put_json(
        '/auctions/{}/documents/{}?acc_token={}'.format(
            self.auction_id, doc_id, self.auction_token
        ), {'data': {'title': u'name.doc',
                     'url': self.generate_docservice_url(),
                     'hash': 'md5:' + '0' * 32,
                     'format': 'application/msword'}}
    )
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertIn('Signature=', response.json["data"]["url"])
    self.assertIn('KeyID=', response.json["data"]["url"])
    self.assertNotIn('Expires=', response.json["data"]["url"])
    key = response.json["data"]["url"].split('/')[-1].split('?')[0]
    auction = self.db.get(self.auction_id)
    self.assertIn(key, auction['documents'][-1]["url"])
    self.assertIn('Signature=', auction['documents'][-1]["url"])
    self.assertIn('KeyID=', auction['documents'][-1]["url"])
    self.assertNotIn('Expires=', auction['documents'][-1]["url"])

    response = self.app.get('/auctions/{}/documents/{}?download={}'.format(
        self.auction_id, doc_id, key))
    self.assertEqual(response.status, '302 Moved Temporarily')
    self.assertIn('http://localhost/get/', response.location)
    self.assertIn('Signature=', response.location)
    self.assertIn('KeyID=', response.location)
    self.assertNotIn('Expires=', response.location)

    response = self.app.get('/auctions/{}/documents/{}'.format(
        self.auction_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual(u'name.doc', response.json["data"]["title"])
    dateModified2 = response.json["data"]['dateModified']
    self.assertTrue(dateModified < dateModified2)
    self.assertEqual(
        dateModified,
        response.json["data"]["previousVersions"][0]['dateModified'])
    self.assertEqual(response.json["data"]['datePublished'], datePublished)

    response = self.app.get(
        '/auctions/{}/documents?all=true'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(dateModified, response.json["data"][0]['dateModified'])
    self.assertEqual(dateModified2, response.json["data"][1]['dateModified'])

    response = self.app.post_json(
        '/auctions/{}/documents?acc_token={}'.format(
            self.auction_id, self.auction_token
        ), {'data': {'title': 'name.doc',
                     'url': self.generate_docservice_url(),
                     'hash': 'md5:' + '0' * 32,
                     'format': 'application/msword'}}
    )
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    dateModified = response.json["data"]['dateModified']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.get('/auctions/{}/documents'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(dateModified2, response.json["data"][0]['dateModified'])
    self.assertEqual(dateModified, response.json["data"][1]['dateModified'])

    response = self.app.put_json(
        '/auctions/{}/documents/{}?acc_token={}'.format(
            self.auction_id, doc_id, self.auction_token
        ), {'data': {'title': u'укр.doc',
                     'url': self.generate_docservice_url(),
                     'hash': 'md5:' + '0' * 32,
                     'format': 'application/msword'}
            }
    )
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertIn('Signature=', response.json["data"]["url"])
    self.assertIn('KeyID=', response.json["data"]["url"])
    self.assertNotIn('Expires=', response.json["data"]["url"])
    key = response.json["data"]["url"].split('/')[-1].split('?')[0]
    auction = self.db.get(self.auction_id)
    self.assertIn(key, auction['documents'][-1]["url"])
    self.assertIn('Signature=', auction['documents'][-1]["url"])
    self.assertIn('KeyID=', auction['documents'][-1]["url"])
    self.assertNotIn('Expires=', auction['documents'][-1]["url"])

    response = self.app.get('/auctions/{}/documents/{}?download={}'.format(
        self.auction_id, doc_id, key))
    self.assertEqual(response.status, '302 Moved Temporarily')
    self.assertIn('http://localhost/get/', response.location)
    self.assertIn('Signature=', response.location)
    self.assertIn('KeyID=', response.location)
    self.assertNotIn('Expires=', response.location)

    self.set_status('active.tendering')

    response = self.app.put_json(
        '/auctions/{}/documents/{}?acc_token={}'.format(
            self.auction_id, doc_id, self.auction_token
        ), {'data': {'title': u'укр.doc',
                     'url': self.generate_docservice_url(),
                     'hash': 'md5:' + '0' * 32,
                     'format': 'application/msword'}
            }, status=403
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(
        response.json['errors'][0]["description"],
        "Can't update document in current (active.tendering) auction status"
    )
