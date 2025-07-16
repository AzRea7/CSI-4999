import React, { useState, useEffect } from "react";
import axios from "axios";

const USER_ID = "demo-user-id-123";

const Tasks = () => {
  const [tasks, setTasks] = useState([]);
  const [creditScore, setCreditScore] = useState("");
  const [refinanceInfo, setRefinanceInfo] = useState("");
  const [houseTitle, setHouseTitle] = useState("");
  const [housePrice, setHousePrice] = useState("");

  useEffect(() => {
  axios
    .get(`${import.meta.env.VITE_API_URL}/tasks`, {
      params: { user_id: USER_ID },
    })
    .then((res) => {
      console.log("API /tasks response:", res.data);
      setTasks(res.data.tasks || []); // <= fallback to empty array
    })
    .catch((err) => {
      console.error("Failed to fetch tasks:", err);
      setTasks([]); // fallback on error
    });
}, []);


  const handleGenerate = (e) => {
    e.preventDefault();

    const fullInfo = `${
      refinanceInfo || "not refinancing"
    }. The house is titled '${houseTitle}' and priced at $${
      housePrice || "N/A"
    }.`;

    axios
      .post(`${import.meta.env.VITE_API_URL}/tasks/generate`, {
        user_id: USER_ID,
        credit_score: creditScore,
        refinancing_info: fullInfo,
      })
      .then((res) => setTasks(res.data.tasks))
      .catch((err) => console.error("Task generation failed:", err));
  };

  const handleComplete = async (taskId) => {
    try {
      await axios.delete(`${import.meta.env.VITE_API_URL}/tasks/${taskId}`);
      setTasks((prev) => prev.filter((t) => t.id !== taskId));
    } catch (err) {
      console.error("Failed to delete task:", err);
    }
  };

  return (
    <div className="px-6 py-10 max-w-5xl mx-auto bg-white min-h-screen">
      <h2 className="text-4xl font-semibold mb-8 text-gray-800">
        Personalized Home Tasks
      </h2>

      <form
        onSubmit={handleGenerate}
        onKeyDown={(e) => {
          if (e.key === "Enter") e.preventDefault(); // Prevent Enter from submitting
        }}
        className="grid md:grid-cols-2 gap-6 mb-12 bg-gray-50 p-6 rounded-2xl shadow-sm"
      >
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Credit Score
          </label>
          <input
            type="number"
            value={creditScore}
            required
            onChange={(e) => setCreditScore(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:outline-none"
            placeholder="e.g. 720"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Refinancing Info
          </label>
          <input
            type="text"
            value={refinanceInfo}
            placeholder="e.g. first-time buyer"
            onChange={(e) => setRefinanceInfo(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:outline-none"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            House Title
          </label>
          <input
            type="text"
            value={houseTitle}
            placeholder="e.g. Cozy Family Home"
            onChange={(e) => setHouseTitle(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:outline-none"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            House Price ($)
          </label>
          <input
            type="number"
            value={housePrice}
            placeholder="e.g. 350000"
            onChange={(e) => setHousePrice(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:outline-none"
          />
        </div>

        <div className="md:col-span-2">
          <button
            type="submit"
            style={{ backgroundColor: "#3B82F6" }}
            className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-3 px-6 rounded-xl transition w-full md:w-auto"
          >
            Generate Tasks
          </button>
        </div>
      </form>

      <div className="grid gap-6 sm:grid-cols-2">
        {tasks.map((task) => (
          <div
            key={task.id}
            className="p-5 bg-white border border-gray-200 rounded-2xl shadow-sm hover:shadow-md transition relative"
          >
            <div className="mb-3">
              <h3 className="text-lg font-medium text-gray-800 mb-1">
                {task.title}
              </h3>
              <div className="text-sm text-gray-600 space-y-1">
                <p>
                  <strong> Category:</strong>{" "}
                  <span className="capitalize">{task.category}</span>
                </p>
                <p>
                  <strong> Due Date:</strong> {task.due_date}
                </p>
                <p>
                  <strong> Priority:</strong>{" "}
                  <span
                    className={
                      task.priority === "high"
                        ? "text-red-600 font-semibold"
                        : task.priority === "medium"
                        ? "text-yellow-600 font-semibold"
                        : "text-gray-600"
                    }
                  >
                    {task.priority}
                  </span>
                </p>
              </div>
            </div>

            {!task.completed && (
              <div className="absolute bottom-4 right-4">
                <button
                  onClick={() => handleComplete(task.id)}
                  className="text-sm text-blue-500 hover:underline"
                >
                  Mark Complete
                </button>
              </div>
            )}
            {task.completed && (
              <div className="absolute bottom-4 right-4 text-green-500 text-sm font-bold">
                ✔️ Completed
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Tasks;
