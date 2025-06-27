import { useState, useEffect } from "react";
import { Routes, Route, Link } from "react-router-dom";
import axios from "axios";
import "./App.css";

// Pages from Yousuf-Tasks
import HomeDashboard from './pages/HomeDashboard';
import Tasks from './pages/Tasks';
import HomeSearch from './pages/HomeSearch';
import ChatBot from './pages/ChatBot';
import Login from './pages/Login';

function App() {
  const [count, setCount] = useState(0);
  const [array, setArray] = useState([]);

  const fetchAPI = async () => {
    try {
      const response = await axios.get("http://localhost:8080/api/users");
      console.log(response.data.users);
      setArray(response.data.users);
    } catch (error) {
      console.error("Failed to fetch users:", error);
    }
  };

  useEffect(() => {
    fetchAPI();
  }, []);

  return (
    <div>
      <nav style={{ padding: '10px', background: '#f4f4f4' }}>
        <Link to="/" style={{ marginRight: '10px' }}>Home</Link>
        <Link to="/tasks" style={{ marginRight: '10px' }}>Tasks</Link>
        <Link to="/search" style={{ marginRight: '10px' }}>Search</Link>
        <Link to="/chatbot" style={{ marginRight: '10px' }}>ChatBot</Link>
        <Link to="/login">Login</Link>
      </nav>

      <Routes>
        <Route path="/" element={<HomeDashboard />} />
        <Route path="/tasks" element={<Tasks />} />
        <Route path="/search" element={<HomeSearch />} />
        <Route path="/chatbot" element={<ChatBot />} />
        <Route path="/login" element={<Login />} />
      </Routes>

      {/* Optional: Retain fetch & counter demo if useful for dev/testing */}
    </div>
  );
}

export default App;
