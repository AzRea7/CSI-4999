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

const USER_ID = "demo-user-id-123";

const Analytics = () => {
  const [homes, setHomes] = useState([]);
  const [selectedHome, setSelectedHome] = useState(null);
  const [forecastData, setForecastData] = useState([]);
  const [confidence, setConfidence] = useState("");

  useEffect(() => {
    axios
      .get(`${import.meta.env.VITE_API_URL}/homes?user_id=${USER_ID}`)
      .then((res) => {
        console.log("Loaded homes:", res.data.homes);
        if (res.data.homes && res.data.homes.length > 0) {
          setHomes(res.data.homes);
        } else {
          // fallback test data
          setHomes([
            {
              _id: "1",
              title: "123 Test Street",
              area: 1400,
              bedrooms: 3,
              bathrooms: 2,
            },
            {
              _id: "2",
              title: "456 Sample Ave",
              area: 1800,
              bedrooms: 4,
              bathrooms: 3,
            },
          ]);
        }
      })
      .catch((err) => {
        console.error("Failed to load homes", err);
        // fallback test data
        setHomes([
          {
            _id: "1",
            title: "123 Test Street",
            area: 1400,
            bedrooms: 3,
            bathrooms: 2,
          },
          {
            _id: "2",
            title: "456 Sample Ave",
            area: 1800,
            bedrooms: 4,
            bathrooms: 3,
          },
        ]);
      });
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

    console.log("Forecast API response:", res.data);
    console.log("Forecast array:", res.data.forecast);

    setForecastData(res.data.forecast || []);
    setConfidence(res.data.confidence || "");
  } catch (err) {
    console.error("Forecast error", err);
  }
};


  return (
    <div className="analytics-container">
      <h2 className="analytics-title">Home Price Forecast</h2>

      {homes.length === 0 && (
        <p style={{ textAlign: "center", color: "gray" }}>
          No homes found for this user.
        </p>
      )}

      <div className="home-cards">
        {homes.map((home) => (
          <div
            key={home._id}
            className={`p-4 bg-white border border-gray-200 rounded-xl shadow-sm cursor-pointer ${
              selectedHome?._id === home._id ? "border-blue-500" : ""
            }`}
            onClick={() => setSelectedHome(home)}
          >
            <h4 className="text-md font-medium text-gray-800">{home.title}</h4>
            <p className="text-sm text-gray-600">
              {home.area} sqft • {home.bedrooms} bd • {home.bathrooms} ba
            </p>
          </div>
        ))}
      </div>

      <div style={{ textAlign: "center", margin: "1.5rem" }}>
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
              <YAxis
                tickFormatter={(value) =>
                  `$${new Intl.NumberFormat("en-US").format(Math.round(value))}`
                }
              />
              <XAxis dataKey="date" label={{ value: "Year", position: "insideBottom", offset: -5 }} />
              <Tooltip 
                formatter={(value) => `$${value.toLocaleString()}`} 
                labelFormatter={(label) => `Year: ${label}`}
              />
              <CartesianGrid stroke="#eee" />
              <Line 
                type="monotone" 
                dataKey="price" 
                stroke="#3B82F6" 
                strokeWidth={2} 
                dot={{ r: 3 }}
              />
            </LineChart>
          </ResponsiveContainer>
          <p className="model-confidence">
            Model Confidence: {confidence || "N/A"}
          </p>
        </div>
      )}
    </div>
  );
};

export default Analytics;
