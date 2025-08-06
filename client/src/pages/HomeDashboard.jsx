import React, { useState, useEffect } from "react";
import axios from "axios";
import { useAuth } from "../AuthContext";

const HomeDashboard = () => {
  const { user } = useAuth();
  const [principal, setPrincipal] = useState("");
  const [interestRate, setInterestRate] = useState("");
  const [years, setYears] = useState("");
  const [monthlyPayment, setMonthlyPayment] = useState(null);

  const [favorites, setFavorites] = useState([]);
  const [tasks, setTasks] = useState([]);   

  const USER_ID = user?.id;

// Fetch tasks and favorite homes for the user on component mount/update
useEffect(() => {
  if (!user?.id) return;

  // Get current tasks for the user
  axios
    .get("http://localhost:5000/api/tasks", {
      params: { user_id: USER_ID },
    })
    .then((res) => setTasks(res.data.tasks))
    .catch((err) => console.error("Failed to fetch tasks:", err));

  // Get favorited homes for the user (✅ use /api/favorites now)
  axios
    .get("http://localhost:5000/api/favorites", {
      params: { userId: USER_ID },
    })
    .then((res) => setFavorites(res.data.favorites || []))
    .catch((err) => {
      console.error("Failed to fetch favorite homes:", err);
      setFavorites([]);
    });
}, [user?.id]);


  const handleCalculate = (e) => {
    e.preventDefault();
    const P = parseFloat(principal);
    const annualInterest = parseFloat(interestRate) / 100;
    const n = parseFloat(years) * 12;
    if (!isNaN(P) && !isNaN(annualInterest) && !isNaN(n) && P > 0 && n > 0) {
      let monthly;
      if (annualInterest === 0) {
        monthly = P / n;
      } else {
        const r = annualInterest / 12;  // monthly interest rate (decimal)
        monthly = (P * r * Math.pow(1 + r, n)) / (Math.pow(1 + r, n) - 1);
      }
      setMonthlyPayment(monthly.toFixed(2));
    } else {
      setMonthlyPayment(null);
    }
  };

  const handleComplete = async (taskId) => {
    try {
      await axios.delete(`http://localhost:5000/api/tasks/${taskId}`);
      setTasks((prev) => prev.filter((t) => t.id !== taskId));
    } catch (err) {
      console.error("Failed to complete task:", err);
    }
  };
  const toggleFavorite = async (home) => {
  if (!user?.id) {
    alert("Please log in to manage favorites.");
    return;
  }

  try {
    await axios.delete(
      `http://localhost:5000/api/favorites/${home._id}`
    );
    const res = await axios.get("http://localhost:5000/api/favorites", {
      params: { userId: user.id },
    });
    setFavorites(res.data.favorites || []);
  } catch (err) {
    console.error("Failed to unfavorite:", err);
  }
};
  return (
    <div className="px-6 py-10 max-w-5xl mx-auto bg-white min-h-screen">
      {/* Dashboard Heading */}
      <h2 className="text-4xl font-semibold mb-2 text-gray-800"> Home Dashboard</h2>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* Mortgage Calculator Card */}
        <div className="bg-gray-50 p-6 rounded-2xl shadow-sm">
          <h3 className="text-xl font-semibold mb-4 text-gray-800">Mortgage Calculator</h3>
          <form onSubmit={handleCalculate} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Loan Amount ($)
              </label>
              <input
                type="number"
                required
                min="0"
                value={principal}
                onChange={(e) => setPrincipal(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:outline-none"
                placeholder="e.g. 350000"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Interest Rate (%)
              </label>
              <input
                type="number"
                required
                min="0"
                step="0.01"
                value={interestRate}
                onChange={(e) => setInterestRate(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:outline-none"
                placeholder="e.g. 3.5"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Loan Term (years)
              </label>
              <input
                type="number"
                required
                min="1"
                value={years}
                onChange={(e) => setYears(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:outline-none"
                placeholder="e.g. 30"
              />
            </div>
            <button
              type="submit"
              style={{ backgroundColor: "#3B82F6" }}
              className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-3 px-6 rounded-xl transition"
            >
              Calculate
            </button>
          </form>
          {monthlyPayment && (
            <p className="mt-4 text-lg font-medium text-gray-800">
              Estimated Monthly Payment:{" "}
              <span className="text-green-600">${monthlyPayment}</span>
            </p>
          )}
        </div>

        {/* Current Tasks Card */}
        <div className="bg-gray-50 p-6 rounded-2xl shadow-sm">
          <h3 className="text-xl font-semibold mb-4 text-gray-800">Current Tasks</h3>
          {tasks.length > 0 ? (
            <ul className="space-y-3">
              {tasks.map((task) => (
                <li
                  key={task.id}
                  className="flex items-center justify-between bg-white border border-gray-200 rounded-xl p-4"
                >
                  <span
                    className={`text-gray-800 ${
                      task.completed ? "line-through text-gray-500" : ""
                    }`}
                  >
                    {task.title}
                  </span>
                  {!task.completed && (
                    <button
                      onClick={() => handleComplete(task.id)}
                      className="text-sm text-blue-500 hover:underline"
                    >
                      Mark Complete
                    </button>
                  )}
                  {task.completed && (
                    <span className="text-sm font-medium text-green-600">✔️ Done</span>
                  )}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-600">No current tasks.</p>
          )}
        </div>

{/* Favorited Homes Card */}
<div className="bg-gray-50 p-6 rounded-2xl shadow-sm">
  <h3 className="text-xl font-semibold mb-4 text-gray-800">Favorited Homes</h3>
  {favorites && favorites.length > 0 ? (
    <div className="space-y-3">
      {favorites.map((home) => (
        <div
          key={home._id}
          className="p-4 bg-white border border-gray-200 rounded-xl shadow-sm flex gap-4"
        >
          <img
            src={home.image || "https://via.placeholder.com/100"}
            alt={home.title}
            className="w-24 h-24 object-cover rounded"
          />
          <div>
            <h4 className="text-md font-medium text-gray-800">{home.title}</h4>
            <p className="text-sm text-gray-600">{home.city}</p>
            <p className="text-sm font-bold text-gray-800">
              ${home.price?.toLocaleString("en-US")}
            </p>
            <p className="text-xs text-gray-500">
              {home.bedrooms} bed / {home.bathrooms} bath
            </p>
          </div>
        </div>
      ))}
    </div>
  ) : (
    <p className="text-gray-600">You have no favorited homes yet.</p>
  )}
</div>  
      </div>
    </div>
  );
};

export default HomeDashboard;
