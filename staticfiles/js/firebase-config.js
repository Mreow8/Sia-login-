// --- Firebase Imports ---
// If you are using ES Modules (recommended):
import { initializeApp } from "https://www.gstatic.com/firebasejs/11.0.1/firebase-app.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/11.0.1/firebase-auth.js";
import { getFirestore } from "https://www.gstatic.com/firebasejs/11.0.1/firebase-firestore.js";
import { getStorage } from "https://www.gstatic.com/firebasejs/11.0.1/firebase-storage.js";

// --- Your Firebase Configuration ---
const firebaseConfig = {
  apiKey: "AIzaSyDqnc_P7S__GT5nAW9eKwubL5gaNu-VeOs",
  authDomain: "sia-project-ef9e5.firebaseapp.com",
  projectId: "sia-project-ef9e5",
  storageBucket: "sia-project-ef9e5.appspot.com",
  messagingSenderId: "476823975418",
  appId: "1:476823975418:web:0f589cbf81d26e1ecccd81",
};

// --- Initialize Firebase ---
const app = initializeApp(firebaseConfig);

// --- Services ---
export const auth = getAuth(app);
export const db = getFirestore(app);
export const storage = getStorage(app);

console.log("Firebase initialized successfully.");
