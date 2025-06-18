import React, { useState } from 'react';

const HomeSearch = () => {
  const [search, setSearch] = useState('');
  const homes = [
    { id: 1, title: 'Modern Condo in Miami', price: '$1,800/mo', beds: 2 },
    { id: 2, title: 'Cozy Apartment in Chicago', price: '$1,400/mo', beds: 1 },
    { id: 3, title: 'House in LA', price: '$2,200/mo', beds: 3 },
  ];

  return (
    <div>
      <h2>🔍 Home Search</h2>
      <input
        type="text"
        placeholder="Search homes..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        style={{ padding: '8px', marginBottom: '16px' }}
      />
      <div>
        {homes
          .filter(home => home.title.toLowerCase().includes(search.toLowerCase()))
          .map(home => (
            <div key={home.id} style={{ border: '1px solid #ccc', padding: '10px', margin: '10px 0' }}>
              <h4>{home.title}</h4>
              <p>{home.price} • {home.beds} beds</p>
            </div>
          ))}
      </div>
    </div>
  );
};

export default HomeSearch;
