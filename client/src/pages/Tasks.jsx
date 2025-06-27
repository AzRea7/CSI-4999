import React, { useState, useEffect } from "react";
import axios from "axios";

const USER_ID = "demo-user-id-123"; // 🔁 Replace with real user ID from login/auth system if available

const Tasks = () => {
  const [tasks, setTasks] = useState([]);
  const [creditScore, setCreditScore] = useState("");
  const [refinanceInfo, setRefinanceInfo] = useState("");

  // Load tasks on page load
  useEffect(() => {
    axios
      .get(`${import.meta.env.VITE_API_URL}/tasks`, {
        params: { user_id: USER_ID },
      })
      .then((res) => setTasks(res.data.tasks))
      .catch((err) => console.error("Failed to fetch tasks:", err));
  }, []);

  const handleGenerate = (e) => {
    e.preventDefault();
    axios
      .post(`${import.meta.env.VITE_API_URL}/tasks/generate`, {
        user_id: USER_ID,
        credit_score: creditScore,
        refinancing_info: refinanceInfo || "not refinancing",
      })
      .then((res) => setTasks(res.data.tasks))
      .catch((err) => console.error("Task generation failed:", err));
  };

  return (
    <div className="p-4 max-w-xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">📋 AI-Generated Tasks</h2>

      <form onSubmit={handleGenerate} className="space-y-4 mb-6">
        <div>
          <label className="block font-medium">Credit Score:</label>
          <input
            type="number"
            value={creditScore}
            required
            onChange={(e) => setCreditScore(e.target.value)}
            className="w-full p-2 border rounded"
          />
        </div>
        <div>
          <label className="block font-medium">Refinancing Info:</label>
          <input
            type="text"
            value={refinanceInfo}
            placeholder="e.g. first-time buyer or refinancing"
            onChange={(e) => setRefinanceInfo(e.target.value)}
            className="w-full p-2 border rounded"
          />
        </div>
        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded"
        >
          Generate Tasks
        </button>
      </form>

      <ul className="space-y-2">
        {tasks.map((task) => (
          <li key={task.id} className="p-3 bg-gray-100 rounded">
            {task.title}
            {task.completed ? " ✔️" : ""}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Tasks;
