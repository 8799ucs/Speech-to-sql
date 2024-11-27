import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';

const firebaseConfig = {
  apiKey: "AIzaSyDXqsTiNaGuWvlu7GQAyUy3fxlNraOo1Yw",
  authDomain: "automation-78fd4.firebaseapp.com",
  projectId: "automation-78fd4",
  storageBucket: "automation-78fd4.appspot.com",
  messagingSenderId: "409377225725",
  appId: "1:409377225725:web:f3f0f83b988025aadd3794",
  measurementId: "G-BJY6SENVMK"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const firestore = getFirestore(app);

export { auth, firestore };