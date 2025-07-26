import React, { useState, useEffect } from "react";
import axios from "axios";
import "../Styles/Analytics.css";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";

const USER_ID = "demo-user-id-123"; // Replace with actual user ID

const Analytics = () => {
  const [homes, setHomes] = useState([]);
  const [selectedHome, setSelectedHome] = useState(null);
  const [forecastData, setForecastData] = useState([]);
  const [confidence, setConfidence] = useState("");

  // Load homes from backend
  useEffect(() => {
    axios
      .get(`${import.meta.env.VITE_API_URL}/homes?user_id=${USER_ID}`)
      .then((res) => setHomes(res.data.homes || []))
      .catch((err) => console.error("Failed to load homes", err));
  }, []);

  const handleForecast = async () => {
    if (!selectedHome) return;

    const { area, bedrooms, bathrooms } = selectedHome;
    try {
      const res = await axios.post(`${import.meta.env.VITE_API_URL}/forecast`, {
        area,
        bedrooms,
        bathrooms,
      });
      setForecastData(res.data.forecast);
      setConfidence(res.data.confidence || "");
    } catch (err) {
      console.error("Forecast error", err);
    }
  };

  return (
    <div className="analytics-container">
      <h2 className="analytics-title">🏡 Home Price Forecast</h2>

      <div className="home-cards">
        {homes.map((home) => (
          <div
            key={home._id}
            className={`home-card ${
              selectedHome?._id === home._id ? "selected" : ""
            }`}
            onClick={() => setSelectedHome(home)}
          >
            <h3>{home.title || "Untitled"}</h3>
            <p>
              {home.area} sqft • {home.bedrooms} bd • {home.bathrooms} ba
            </p>
          </div>
        ))}
      </div>

      <div style={{ textAlign: "center", margin: "1rem" }}>
        <button
          className="forecast-button"
          onClick={handleForecast}
          disabled={!selectedHome}
        >
          Forecast
        </button>
      </div>

      {forecastData.length > 0 && (
        <div className="forecast-section">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={forecastData}>
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <CartesianGrid stroke="#eee" />
              <Line
                type="monotone"
                dataKey="price"
                stroke="#ff5a5f"
                strokeWidth={2}
                dot={{ r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
          <p className="model-confidence">
            Model Confidence: {confidence || "N/A"}%
          </p>
        </div>
      )}
    </div>
  );
};

export default Analytics;
