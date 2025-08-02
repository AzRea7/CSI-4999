import React, { useState } from 'react';
import axios from 'axios';
import { useAuth } from '../AuthContext';

const Search = () => {
  const { user } = useAuth(); // Assuming useAuth is available
  const [search, setSearch] = useState('');
  const [homes, setHomes] = useState([]);
  const [error, setError] = useState(null);

  const performSearch = async () => {
    setError(null);
    try {
      const resp = await axios.get("http://localhost:5000/api/search", {
        params: { q: search },
      });
      setHomes(resp.data.results || []);
    } catch (err) {
      console.error(err);
      setError("Search failed. Try again.");
    }
  };

const addFavorite = async (home) => {
    if (!user?.id) {
      alert("You must be logged in to favorite a home.");
      return;
    }
    try {
      await axios.post("http://localhost:5000/api/favorites", {
        userId: user.id, // ✅ real logged-in user ID
        zpid: home.id,
        title: home.title,
        city: home.city,
        price: home.price,
        bedrooms: home.bedrooms,
        bathrooms: home.bathrooms,
        image: home.image
      });
      alert("Added to favorites!");
    } catch (err) {
      console.error(err);
      alert("Failed to add favorite.");
    }
  };

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-4">Search Homes</h2>
      <div className="flex gap-2 mb-4">
        <input
          type="text"
          placeholder="Enter city, address, or Zillow ID..."
          className="border p-2 rounded w-full"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && performSearch()}
        />
        <button
          className="bg-blue-500 text-white px-4 py-2 rounded"
          onClick={performSearch}
        >
          Search
        </button>
      </div>

      {error && <p className="text-red-500">{error}</p>}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {homes.map((home) => (
          <div
            key={home.id}
            className="border p-4 rounded shadow hover:shadow-md transition"
          >
            <img
              src={home.image || "https://via.placeholder.com/300"}
              alt={home.title}
              className="w-full h-40 object-cover mb-2 rounded"
            />
            <h3 className="font-semibold">{home.title}</h3>
            <p className="text-sm text-gray-600">{home.city}</p>
            <p className="font-bold">${home.price}</p>
            <p className="text-sm">
              {home.bedrooms} bed / {home.bathrooms} bath
            </p>
            {/* Favorite button */}
            <button
              className="bg-yellow-500 text-white px-3 py-1 rounded mt-2 hover:bg-yellow-600"
              onClick={() => addFavorite(home)}
              style={{ backgroundColor: "#3B82F6" }}
            >
              Favorite
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Search;
