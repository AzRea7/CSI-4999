import React, { useState, useEffect } from "react";
import axios from "axios";
import { useAuth } from "../AuthContext";
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

const Analytics = () => {
  const { user } = useAuth();
  const [favorites, setFavorites] = useState([]);
  const [selectedHome, setSelectedHome] = useState(null);
  const [forecastData, setForecastData] = useState([]);
  const [confidence, setConfidence] = useState("");

  useEffect(() => {
    if (!user?.id) return;
    fetchFavorites();
  }, [user?.id]);

  const fetchFavorites = async () => {
    try {
      const res = await axios.get(`${import.meta.env.VITE_API_URL}/favorites`, {
        params: { userId: user.id },
      });
      setFavorites(res.data.favorites || []);
    } catch (err) {
      console.error("Failed to load favorites", err);
      setFavorites([]);
    }
  };

  const isFavorited = (homeId) => {
    return favorites.find((fav) => fav.zpid === homeId || fav._id === homeId);
  };

  const toggleFavorite = async (home) => {
    const zpid = home.id || home.zpid;
    const existing = favorites.find((fav) => fav.zpid === zpid);

    if (!user?.id) {
      alert("Please login to favorite.");
      return;
    }

    try {
      if (existing) {
        // Unfavorite using MongoDB _id
        await axios.delete(`${import.meta.env.VITE_API_URL}/favorites/${existing._id}`);
      } else {
        // Favorite
        await axios.post(`${import.meta.env.VITE_API_URL}/favorites`, {
          userId: user.id,
          zpid,
          title: home.title,
          city: home.city,
          price: home.price,
          bedrooms: home.bedrooms,
          bathrooms: home.bathrooms,
          image: home.image,
        });
      }
      await fetchFavorites(); // Refresh favorites
    } catch (err) {
      console.error("Favorite toggle failed:", err);
    }
  };

  const handleForecast = async () => {
    if (!selectedHome) return;

    const { price, bedrooms, bathrooms } = selectedHome;

    try {
      const res = await axios.post(`${import.meta.env.VITE_API_URL}/forecast`, {
        price,
        bedrooms,
        bathrooms,
        area: selectedHome.area || 1500,
      });

      setForecastData(res.data.forecast || []);
      setConfidence(res.data.confidence || "");
    } catch (err) {
      console.error("Forecast error", err);
    }
  };

  return (
    <div className="analytics-container">
      <h2 className="analytics-title">Home Price Forecast</h2>

      {favorites.length === 0 && (
        <p style={{ textAlign: "center", color: "gray" }}>
          No favorited homes found.
        </p>
      )}

      <div className="home-cards">
        {favorites.map((home) => (
          <div
            key={home._id}
            className={`p-4 bg-white border border-gray-200 rounded-xl shadow-sm cursor-pointer ${
              selectedHome?._id === home._id ? "border-blue-500 ring-2 ring-blue-300" : ""
            }`}
            onClick={() => setSelectedHome(home)}
          >
            <h4 className="text-md font-medium text-gray-800">{home.title}</h4>
            <p className="text-sm text-gray-600">
              ${home.price?.toLocaleString()} • {home.bedrooms} bd • {home.bathrooms} ba
            </p>
            <p className="text-xs text-gray-400">{home.city}</p>

            {/* ⭐ Favorite/Unfavorite toggle button */}
            <button
              className="text-sm text-blue-600 hover:underline mt-1"
              onClick={(e) => {
                e.stopPropagation(); 
                toggleFavorite(home);
              }}
            >
              {isFavorited(home.zpid || home._id) ? "★ Unfavorite" : "☆ Favorite"}
            </button>
          </div>
        ))}
      </div>

      <div style={{ textAlign: "center", margin: "1.5rem" }}>
        <button
          className="forecast-button"
          onClick={handleForecast}
          disabled={!selectedHome}
        >
          Forecast Selected Home
        </button>
      </div>

      {forecastData.length > 0 && (
        <div className="forecast-section">
          <h3 className="text-xl font-semibold text-gray-700 mb-2">
            Forecast for: {selectedHome?.title}
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart
              data={forecastData}
              margin={{ top: 20, right: 30, left: 60, bottom: 10 }}
            >
              <YAxis
                tickFormatter={(value) =>
                  `$${new Intl.NumberFormat("en-US").format(Math.round(value))}`
                }
              />
              <XAxis dataKey="date" />
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
