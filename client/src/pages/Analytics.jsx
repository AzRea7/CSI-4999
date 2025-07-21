import React, { useState } from 'react';

const Analytics = () => {
  const [area, setArea] = useState('');
  const [bedrooms, setBedrooms] = useState('');
  const [bathrooms, setBathrooms] = useState('');
  const [forecastData, setForecastData] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const payload = {
      area: Number(area), 
      bedrooms: Number(bedrooms), 
      bathrooms: Number(bathrooms),
    };
    try {
      const res = await fetch('/api/forecast', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      setForecastData(data.forecast);
    } catch (err) {
      console.error("Error fetching forecast:", err);
    }
  };

  return (
    <div>
      <h2> Price Forecast</h2>
      <form onSubmit={handleSubmit} style={{ maxWidth: '400px', marginBottom: '20px' }}>
        <div>
          <label>Area (sqft): </label>
          <input type="number" value={area} onChange={e => setArea(e.target.value)} required />
        </div>
        <div>
          <label>Bedrooms: </label>
          <input type="number" value={bedrooms} onChange={e => setBedrooms(e.target.value)} required />
        </div>
        <div>
          <label>Bathrooms: </label>
          <input type="number" value={bathrooms} onChange={e => setBathrooms(e.target.value)} required />
        </div>
        <button type="submit">Predict Price</button>
      </form>
    </div>
  );
};

export default Analytics;