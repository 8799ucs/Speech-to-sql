import React, { useState } from 'react';
import { signInWithEmailAndPassword } from 'firebase/auth';
import { auth} from './Firebase';
import { useNavigate } from 'react-router-dom';
import { createUserWithEmailAndPassword } from 'firebase/auth';
import './Login.css';
import axios from "axios";



function Login() {
  const [isLogin, setIsLogin] = useState(true); // State to toggle between login and signup
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [message, setMessage] = useState('');
  const navigate = useNavigate();


  const handleLogin = (e) => {
    e.preventDefault();
    try {
        const userCredential = signInWithEmailAndPassword(auth, username, password);
        const user = userCredential.user;
        console.log(user);
        navigate("/Home");
        
      } catch (err) {
        console.log(err.message);
      }
    
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    try {
        createUserWithEmailAndPassword(auth, username, password);
        // Handle successful  
        const response =  await axios.post("http://localhost:5000/generate", {
            username,
          });
        console.log(response)
        navigate("/Home")
        console.log('User created successfully');
      } catch (error) {
        console.log(error.message);
      }
    if (password !== confirmPassword) {
      setMessage('Passwords do not match!');
    } else if (username && password) {
      setMessage('Signup Successful!');

    } else {
      setMessage('Please fill out all fields.');
    }
  };

  return (
    <div className="App">
      <h1>Welcome to the Authentication Portal</h1>
      <div className="login-container">
        <div>
          {/* Toggle Buttons */}
          <button
            className={`toggle-button ${isLogin ? 'active' : ''}`}
            onClick={() => {
              setIsLogin(true);
              setMessage('');
            }}
          >
            Login
          </button>
          <button
            className={`toggle-button ${!isLogin ? 'active' : ''}`}
            onClick={() => {
              setIsLogin(false);
              setMessage('');
            }}
          >
            Signup
          </button>
        </div>

        <div className="login-box">
          {isLogin ? (
            /* Login Form */
            <form onSubmit={handleLogin}>
              <h2>Login</h2>
              <label htmlFor="username">Username:</label>
              <input
                type="text"
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
              <label htmlFor="password">Password:</label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <button className='l-button' type="submit">Login</button>
            </form>
          ) : (
            /* Signup Form */
            <form onSubmit={handleSignup}>
              <h2>Signup</h2>
              <label htmlFor="username">Username:</label>
              <input
                type="text"
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
              <label htmlFor="password">Password:</label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <label htmlFor="confirmPassword">Confirm Password:</label>
              <input
                type="password"
                id="confirmPassword"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
              />
              <button className='l-button' type="submit">Signup</button>
            </form>
          )}
          {message && <p className="message">{message}</p>}
        </div>
      </div>
    </div>
  );
}

export default Login;
