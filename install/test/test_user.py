from unittest import TestCase, skip
import requests

try:
    from settings import API_BASE_URL
except ImportError:
    import os, sys
    DIR = os.path.dirname(__file__)
    sys.path.append(os.path.join(DIR, '..'))
    from settings import API_BASE_URL

class TestUser(TestCase):

    def test_get_all(self):
        url = f'{API_BASE_URL}/user'
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)
        json = response.json()
        self.assertIsInstance(json, dict)
        self.assertIn('result', json)
        self.assertIsInstance(json['result'], list)

    def test_get_one(self):
        url = f'{API_BASE_URL}/user'
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)
        json = response.json()
        test_user = json['result'][0]
        user_id = test_user['user_id']
        url_one = f'{url}/{user_id}'
        response_one = requests.get(url_one)
        self.assertEqual(response_one.status_code, 200)
        json1 = response_one.json()
        self.assertIsInstance(json1, dict)
        self.assertIn('user_id', json1)
        self.assertEquals(json1['user_id'], user_id)
        
    def test_create(self):
        url = f'{API_BASE_URL}/user'
        dummy = {'first_name': 'Freddie', 'last_name': "Farkle", 'color': 'flame', 'test item':'delete me'}

        # Create item
        response = requests.post(url, json=dummy)
        self.assertEqual(response.status_code, 200)
        json = response.json()
        self.assertIsInstance(json, dict)
        self.assertIn('user_id', json)
        new_id = json['user_id']

        # Verify item was created
        new_url = f'{url}/{new_id}'
        response_check = requests.get(new_url)
        new_item = response_check.json()
        dummy2 = dummy.copy()
        dummy2['user_id'] = new_id
        self.assertDictEqual(new_item, dummy2)

        # Delete test item
        response_del = requests.delete(new_url)
        self.assertEquals(response_del.status_code, 200)

        # Verify deletion
        response_gone = requests.get(new_url)
        self.assertEquals(response_gone.status_code, 404)

    def test_update(self):
        url = f'{API_BASE_URL}/user'
        dummy1 = {"first_name": "Charlie", "last_name": "L'Tuna", "color": "silver", "test item": "delete me"}
        update_data = {'first_name': 'Sally', 'color': 'shiny silver'}
        dummy2 = {'first_name': 'Sally', 'last_name': "L'Tuna", 'color': 'shiny silver', 'test item':'delete me'}

        # Create item
        response = requests.post(url, json=dummy1)
        self.assertEqual(response.status_code, 200)
        json = response.json()
        self.assertIsInstance(json, dict)
        self.assertIn('user_id', json)
        new_id = json['user_id']

        # Modify item
        new_url = f'{url}/{new_id}'
        response_mod = requests.put(new_url, json=update_data)
        self.assertEqual(response_mod.status_code, 200)

        # Verify changed item
        compare = dummy2.copy()
        compare['user_id'] = new_id
        response_check = requests.get(new_url)        
        compare_item = response_check.json()
        self.assertDictEqual(compare_item, compare)

        # Delete test item
        response_del = requests.delete(new_url)
        self.assertEquals(response_del.status_code, 200)

        # Verify deletion
        response_gone = requests.get(new_url)
        self.assertEquals(response_gone.status_code, 404)
