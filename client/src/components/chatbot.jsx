import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';

const Chatbot = () => {
  const [message, setMessage] = useState('');
  const [chat, setChat] = useState([]);
  const messagesEndRef = useRef(null);

  const sendMessage = async () => {
    if (!message.trim()) return;

    const newChat = [...chat, { sender: 'user', text: message }];
    setChat(newChat);
    setMessage('');

    try {
      const res = await axios.post('http://localhost:5000/api/chat', { message });
      const reply = res.data.reply;
      setChat([...newChat, { sender: 'bot', text: reply }]);
    } catch (err) {
      console.error('Chat error:', err);
      setChat([...newChat, { sender: 'bot', text: 'Something went wrong. Please try again.' }]);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') sendMessage();
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chat]);

  return (
    <div className="p-4 max-w-2xl mx-auto bg-black rounded shadow-lg">
      <h2 className="text-2xl font-bold mb-4 text-center text-white">Ask our Real Estate Chatbot</h2>

      <div className="h-80 overflow-y-auto border p-4 mb-4 bg-gray-100 rounded space-y-3">
        {chat.length === 0 ? (
          <p className="text-gray-500 text-sm italic">Ask a question like “How do I get a mortgage?”</p>
        ) : (
          chat.map((msg, i) => (
            <div
              key={i}
              className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`p-3 rounded-lg max-w-[70%] ${
                  msg.sender === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-300 text-black'
                }`}
              >
                {msg.text}
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          className="flex-1 p-2 border rounded focus:outline-none focus:ring bg-white text-black"
          placeholder="Type your message and hit Enter..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button
          onClick={sendMessage}
          className="bg-black text-black px-5 py-2 rounded hover:bg-gray-800"
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default Chatbot;
