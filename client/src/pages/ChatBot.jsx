import { useState } from "react";
import axios from "axios";

const ChatBot = () => {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);

  const handleSend = async () => {
    if (!input.trim()) return;

    setMessages((prev) => [...prev, { role: "user", text: input }]);

    try {
      const res = await axios.post("http://localhost:5050/api/chat", {
        message: input,
      });

      const reply = res.data.reply || "No response received.";
      setMessages((prev) => [
        ...prev,
        { role: "user", text: input },
        { role: "bot", text: reply },
      ]);
    } catch (error) {
      console.error("Chatbot error:", error);
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: "⚠️ Failed to reach chatbot API." },
      ]);
    }

    setInput("");
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold mb-4"> ChatBot</h2>

      <div className="border rounded-lg p-4 h-64 overflow-y-auto bg-gray-50 mb-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`mb-2 ${
              msg.role === "user" ? "text-right" : "text-left"
            }`}
          >
            <span
              className={`inline-block px-3 py-2 rounded ${
                msg.role === "user"
                  ? "bg-blue-200 text-blue-800"
                  : "bg-gray-200 text-gray-800"
              }`}
            >
              {msg.text}
            </span>
          </div>
        ))}
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-1 p-2 border rounded"
          placeholder="Type a message..."
        />
        <button
          onClick={handleSend}
          className="bg-green-500 text-white px-4 py-2 rounded"
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatBot;
