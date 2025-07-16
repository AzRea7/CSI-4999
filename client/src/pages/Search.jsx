import { useState } from "react";
import axios from "axios";

const Search = () => {
  const [query, setQuery] = useState("");
  const [homes, setHomes] = useState([]);
  const [error, setError] = useState(null);

  const handleSearch = async () => {
    setError(null);
    try {
      const response = await axios.get("http://localhost:5050/api/search", {
        params: { q: query },
        withCredentials: false,
      });
      setHomes(response.data.results);
    } catch (err) {
      console.error(err);
      setError("Search failed. Try again.");
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Search Homes</h1>
      <div className="flex gap-2 mb-4">
        <input
          type="text"
          placeholder="Enter city or title..."
          className="p-2 border rounded w-full"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button
          className="bg-blue-500 text-white px-4 py-2 rounded"
          onClick={handleSearch}
        >
          Search
        </button>
      </div>

      {error && <div className="text-red-500 mb-2">{error}</div>}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {homes.map((home) => (
          <div
            key={home.id}
            className="border p-4 rounded shadow hover:shadow-md transition"
          >
            <img
              src={home.image || "https://via.placeholder.com/150"}
              alt={home.title}
              className="w-full h-40 object-cover mb-2 rounded"
            />
            <h2 className="text-lg font-semibold">{home.title}</h2>
            <p>City: {home.city}</p>
            <p>Price: ${home.price}</p>
            <p>{home.bedrooms} bed / {home.bathrooms} bath</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Search;
