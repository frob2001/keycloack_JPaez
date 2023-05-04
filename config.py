import pyrebase

config = {
  "apiKey": "AIzaSyB_l89ywSTO1KHvV5ogxx_CniLSfx2p5S4",
  "authDomain": "jpaezdemo.firebaseapp.com",
  "databaseURL": "https://jpaezdemo-default-rtdb.firebaseio.com",
  "projectId": "jpaezdemo",
  "storageBucket": "jpaezdemo.appspot.com",
  "messagingSenderId": "175584888592",
  "appId": "1:175584888592:web:d8ae6447fe91eedcf7c795",
  "measurementId": "G-VKGPDPGLXS"
}

firebase = pyrebase.initialize_app(config)
fdb = firebase.database()
auth = firebase.auth()