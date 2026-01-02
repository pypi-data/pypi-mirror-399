from tests.client import FixturesTestCase


class TestTenantsAPI(FixturesTestCase):
    user_id = FixturesTestCase.OWNER_USER_ID

    def test_list_all_tenants(self):
        self.force_login()
        resp = self.client.get('/m/tenants/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIsInstance(data, list)

    def test_create_tenant(self):
        self.force_login()
        data = {'name': 'Demo', 'slug': 'demo'}
        resp = self.client.post('/m/tenants/', data=data)
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertEqual(data['name'], 'Demo')

    def test_fetch_tenant(self):
        self.force_login()
        resp = self.client.get('/m/tenants/1/')
        self.assertEqual(resp.status_code, 200)

    def test_update_tenant(self):
        self.force_login()
        data = {'name': 'Demo 2'}
        resp = self.client.patch('/m/tenants/1/', data=data)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['name'], 'Demo 2')

    def test_cannot_update_readonly_fields(self):
        self.force_login()
        data = {'slug': 'demo-2', 'region': 'uk'}
        resp = self.client.patch('/m/tenants/1/', data=data)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['slug'], 'demo-1')
        self.assertEqual(data['region'], 'us')


class TestTenantsUsingGuestUser(FixturesTestCase):
    user_id = FixturesTestCase.GUEST_USER_ID

    def test_fetch_tenant(self):
        self.force_login()
        resp = self.client.get('/m/tenants/1/')
        self.assertEqual(resp.status_code, 403)

    def test_update_tenant(self):
        self.force_login()
        data = {'name': 'Demo 2'}
        resp = self.client.patch('/m/tenants/1/', data=data)
        self.assertEqual(resp.status_code, 403)
