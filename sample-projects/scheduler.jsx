import React, { useState, useEffect } from 'react';
import { Calendar, Clock, Trash2, Mic, Send } from 'lucide-react';

export default function AISchedulerAgent() {
  const [input, setInput] = useState('');
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [todayItems, setTodayItems] = useState([]);
  const [isListening, setIsListening] = useState(false);

  useEffect(() => {
    loadItems();
  }, []);

  useEffect(() => {
    updateTodayItems();
  }, [items]);

  const loadItems = async () => {
    try {
      const keys = await window.storage.list('scheduler:');
      if (keys && keys.keys) {
        const loadedItems = [];
        for (const key of keys.keys) {
          const result = await window.storage.get(key);
          if (result) {
            loadedItems.push(JSON.parse(result.value));
          }
        }
        setItems(loadedItems.sort((a, b) => new Date(a.date) - new Date(b.date)));
      }
    } catch (error) {
      console.log('No existing items found');
    }
  };

  const updateTodayItems = () => {
    const today = new Date().toISOString().split('T')[0];
    const filtered = items.filter(item => item.date === today);
    setTodayItems(filtered);
  };

  const parseWithAI = async (text) => {
    setLoading(true);
    try {
      const response = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: "claude-sonnet-4-20250514",
          max_tokens: 1000,
          system: `You are a scheduling assistant. Parse the user's natural language input and extract appointments or reminders. Return ONLY a JSON object with this exact structure (no other text, no markdown):
{
  "items": [
    {
      "type": "appointment" or "reminder",
      "title": "brief description",
      "date": "YYYY-MM-DD format",
      "time": "HH:MM format or null if not specified"
    }
  ]
}

Current date: ${new Date().toISOString().split('T')[0]}

Examples:
- "Dentist appointment tomorrow at 3pm" → date: tomorrow's date, time: "15:00"
- "Remind me to call mom on Friday" → type: reminder, date: next Friday
- "Meeting on December 15th at 10am" → date: "2025-12-15", time: "10:00"
- "Dinner with Sarah next Monday" → date: next Monday's date`,
          messages: [
            { role: "user", content: text }
          ],
        })
      });

      const data = await response.json();
      const aiResponse = data.content.find(c => c.type === 'text')?.text || '';
      const cleanResponse = aiResponse.replace(/```json|```/g, '').trim();
      const parsed = JSON.parse(cleanResponse);

      if (parsed.items && parsed.items.length > 0) {
        const newItems = [];
        for (const item of parsed.items) {
          const newItem = {
            id: Date.now() + Math.random(),
            ...item,
            created: new Date().toISOString()
          };
          await window.storage.set(`scheduler:${newItem.id}`, JSON.stringify(newItem));
          newItems.push(newItem);
        }
        setItems(prev => [...prev, ...newItems].sort((a, b) => new Date(a.date) - new Date(b.date)));
        setInput('');
      }
    } catch (error) {
      console.error('Error parsing:', error);
      alert('Could not understand the request. Please try again.');
    }
    setLoading(false);
  };

  const deleteItem = async (id) => {
    try {
      await window.storage.delete(`scheduler:${id}`);
      setItems(prev => prev.filter(item => item.id !== id));
    } catch (error) {
      console.error('Error deleting:', error);
    }
  };

  const handleVoiceInput = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert('Voice input not supported in your browser');
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;

    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInput(transcript);
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      setIsListening(false);
    };

    recognition.start();
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr + 'T00:00:00');
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    if (date.toDateString() === today.toDateString()) return 'Today';
    if (date.toDateString() === tomorrow.toDateString()) return 'Tomorrow';
    
    return date.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-6">
          <h1 className="text-3xl font-bold text-gray-800 mb-2 flex items-center gap-3">
            <Calendar className="text-indigo-600" size={36} />
            AI Scheduler Agent
          </h1>
          <p className="text-gray-600 mb-6">Tell me about your appointments and reminders using natural language</p>

          {/* Today's Items */}
          {todayItems.length > 0 && (
            <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl p-6 mb-6 text-white">
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Clock size={24} />
                Today's Schedule
              </h2>
              <div className="space-y-3">
                {todayItems.map(item => (
                  <div key={item.id} className="bg-white bg-opacity-20 rounded-lg p-4 backdrop-blur">
                    <div className="flex justify-between items-start">
                      <div>
                        <span className="text-sm font-semibold uppercase tracking-wide opacity-90">
                          {item.type}
                        </span>
                        <p className="text-lg font-medium">{item.title}</p>
                        {item.time && <p className="text-sm opacity-90">at {item.time}</p>}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Input Section */}
          <div className="mb-6">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && !loading && input.trim() && parseWithAI(input)}
                placeholder="e.g., 'Dentist appointment tomorrow at 3pm' or 'Remind me to call John on Friday'"
                className="flex-1 px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-indigo-500"
                disabled={loading}
              />
              <button
                onClick={handleVoiceInput}
                className={`px-4 py-3 rounded-lg transition ${
                  isListening 
                    ? 'bg-red-500 text-white' 
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
                disabled={loading}
              >
                <Mic size={20} />
              </button>
              <button
                onClick={() => parseWithAI(input)}
                disabled={loading || !input.trim()}
                className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition flex items-center gap-2"
              >
                {loading ? 'Processing...' : <><Send size={20} /> Add</>}
              </button>
            </div>
          </div>

          {/* All Items List */}
          <div>
            <h2 className="text-xl font-bold text-gray-800 mb-4">All Scheduled Items</h2>
            {items.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No appointments or reminders yet. Add one above!</p>
            ) : (
              <div className="space-y-3">
                {items.map(item => (
                  <div key={item.id} className="bg-gray-50 rounded-lg p-4 flex justify-between items-center hover:bg-gray-100 transition">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-1">
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          item.type === 'appointment' 
                            ? 'bg-blue-100 text-blue-800' 
                            : 'bg-green-100 text-green-800'
                        }`}>
                          {item.type}
                        </span>
                        <span className="text-gray-600 font-medium">{formatDate(item.date)}</span>
                        {item.time && <span className="text-gray-500">• {item.time}</span>}
                      </div>
                      <p className="text-gray-800 font-medium">{item.title}</p>
                    </div>
                    <button
                      onClick={() => deleteItem(item.id)}
                      className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition"
                    >
                      <Trash2 size={18} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <p className="text-center text-gray-600 text-sm">
          💡 Try: "Meeting with Sarah tomorrow at 2pm" or "Remind me to buy groceries on Saturday"
        </p>
      </div>
    </div>
  );
}
