import json
import unittest
import requests

from io import BytesIO
from PIL import Image

class Config:
    def __init__(self):
        self.testUser = 'testuser'
        self.testPassword = 'password'
        self.testPictures = ['1.png', '2.jpg', '3.tif']
        self.rootURL = "http://localhost:9000/api/"
        # 8000 is the production server, 9000 is the testserver

class RESTTestCase(unittest.TestCase):

    def setUp(self):
        self.config = Config()

    def deleteUser(self, user, password):
        # Delete a user
        endpoint = self.config.rootURL + "deleteUser"
        session = self.login(user, password)
        r = session.post(endpoint)

        assert(r.status_code == 200 or r.status_code == 404)
        session.close()

    def login(self, user, password):
        # Provides a logged in session
        session = requests.Session()
        endpoint = self.config.rootURL + "login"
        data = {'username': user,
                'password': password}

        r = session.post(endpoint, data)
        assert(r.status_code == 200)
        return session

    def uploadPicture(self, username, password, pic):
        # Upload a picture
        endpoint = self.config.rootURL + 'uploadPicture'
        session = self.login(username, password)
        files = {'picture': pic}
        session.post(endpoint, files=files)
        return session
 
    def testCreateUser(self):
        # Test creating a user
        #
        # Test with well formed request, malformed request
        # and existing user

        endpoint = self.config.rootURL + "createUser"

        incorrectData = {'username': self.config.testUser,
                         'password': self.config.testPassword}

        data = {'username': self.config.testUser,
                'password': self.config.testPassword,
                'email': 'testuser@email.com'}

        self.deleteUser(self.config.testUser, self.config.testPassword)

        r = requests.post(endpoint, data = incorrectData)
        assert(r.status_code == 400) # Bad request

        # First try should be successful, make sure fixture is fresh
        r = requests.post(endpoint, data = data)
        assert(r.status_code == 200) # OK
        
        # Second try should not work
        r = requests.post(endpoint, data = data)
        assert(r.status_code == 409) # Conflict

    def testLogin(self):
        # Test user login and access to protected page

        session = requests.Session()
        endpoint = self.config.rootURL + "createUser"
        data = {'username': self.config.testUser,
                'password': self.config.testPassword,
                'email': 'testuser@email.com'}
        r = requests.post(endpoint, data = data)
        assert(r.status_code == 200 or r.status_code == 409) # OK or already exists

        endpoint = self.config.rootURL + "protected"
        r = session.post(endpoint)
        assert(r.status_code == 404)

        endpoint = self.config.rootURL + "login"
        data = {'username': self.config.testUser,
                'password': self.config.testPassword}

        r = session.post(endpoint, data)
        assert(r.status_code == 200)

        endpoint = self.config.rootURL + "protected"
        r = session.post(endpoint)
        assert(r.status_code == 200)
        session.close()

    def testUploadPicture(self):
        # Test uploading a PNG/JPEG/TIFF picture,
        #
        # Only PNG and JPEG will be accepted

        endpoint = self.config.rootURL + 'uploadPicture'

        session = self.login(self.config.testUser, self.config.testPassword)
        for pic in self.config.testPictures[:2]:
            f = open(pic, 'rb')
            picture = {'picture': f}
            r = session.post(endpoint, files=picture)
            assert(r.status_code == 200)
            f.close()

        f = open(self.config.testPictures[2], 'rb') # TIFF picture
        picture = {'picture': f}
        r = session.post(endpoint, files=picture)
        f.close()
        assert(r.status_code == 400)

        r = session.post(endpoint)
        assert(r.status_code == 400) # Missing the picture
        session.close()

    def testGetPictureFunctions(self):
        # Test getting the picture list, getting individual picture and getting a processed picture.

        endpoint = self.config.rootURL + 'getPictureList'
        f = open(self.config.testPictures[0], 'rb')
        session = self.uploadPicture(self.config.testUser, self.config.testPassword, f)

        r = session.post(endpoint)
        assert(r.status_code == 200)
        picList = json.loads(r.text)
        assert(picList['pictures'] != [])

        picId = picList['pictures'][0]
        endpoint = self.config.rootURL + 'getPicture'
        data = {'id': picId}

        r = session.post(endpoint, data = data)
        assert(r.status_code == 200)
        i = Image.open(BytesIO(r.content))
        oi = Image.open(self.config.testPictures[0])
        assert(i == oi)
        
        # We have to run this helper function to move the picture into the processed state with a no-op
        # the regular processing is expensive in time and money so we use a no-op

        endpoint = self.config.rootURL + 'testProcessAllNewTasks'
        r = session.post(endpoint)
        assert(r.status_code == 200)

        endpoint = self.config.rootURL + 'getPictureProcessed'
        data = {'id': picId}

        r = session.post(endpoint, data = data)
        assert(r.status_code == 200)
        i = Image.open(BytesIO(r.content))
        oi = Image.open(self.config.testPictures[0])

        # Typically the processed picture would be different
        # but we used the testHelper function that processes
        # them with a no-op
        assert(i == oi)

        f.close()
        session.close()

    def testLogout(self):
        # Test logging out and accessing a protected page after logout

        session = self.login(self.config.testUser, self.config.testPassword)
        endpoint = self.config.rootURL + 'protected'
        r = session.post(endpoint)
        assert(r.status_code == 200)

        endpoint = self.config.rootURL + 'logout'
        r = session.post(endpoint)
        assert(r.status_code == 200)

        endpoint = self.config.rootURL + 'protected'
        r = session.post(endpoint)
        assert(r.status_code == 404)

if __name__ == "__main__":
    unittest.main()
