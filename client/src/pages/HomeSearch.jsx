import { useState } from "react";
import axios from "axios";

function HomeSearch() {
  const [city, setCity] = useState("");
  const [homes, setHomes] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!city.trim()) return;
    setLoading(true);
    try {
      const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/homes?city=${city}`);
      setHomes(response.data.homes);
    } catch (error) {
      console.error("Failed to fetch homes:", error);
      setHomes([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4 text-center">Search Homes</h1>

      <div className="flex gap-2 mb-4">
        <input
          type="text"
          placeholder="Enter city..."
          value={city}
          onChange={(e) => setCity(e.target.value)}
          className="flex-1 p-2 border rounded"
        />
        <button
          onClick={handleSearch}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Search
        </button>
      </div>

      {loading && <p className="text-center">Loading...</p>}

      <div className="space-y-3">
        {homes.map((home) => (
          <div key={home.id} className="p-4 border rounded shadow">
            <h2 className="text-lg font-semibold">{home.title}</h2>
            <p className="text-gray-600">${home.price}</p>
            {home.image && (
              <img src={home.image} alt={home.title} className="mt-2 w-full h-auto rounded" />
            )}
          </div>
        ))}
        {homes.length === 0 && !loading && (
          <p className="text-center text-gray-500">No results. Try another city.</p>
        )}
      </div>
    </div>
  );
}

export default HomeSearch;
