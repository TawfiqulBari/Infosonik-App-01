import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [note, setNote] = useState({ title: '', content: '', language: 'en' });
  const [event, setEvent] = useState({
    title: '',
    description: '',
    start_time: '',
    end_time: ''
  });

  const handleNoteSubmit = async () => {
    try {
      await axios.post('/notes/', note);
      alert('Note created successfully!');
    } catch (error) {
      console.error(error);
    }
  };

  const handleEventSubmit = async () => {
    try {
      // In a real app, you'd handle Google OAuth here
      const credentials = { token: 'user_token' };
      await axios.post('/events/', { ...event, credentials });
      alert('Event created successfully!');
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="App">
      <h1>Notes & Calendar App</h1>
      
      <div>
        <h2>Create Note</h2>
        <input
          placeholder="Title"
          value={note.title}
          onChange={(e) => setNote({...note, title: e.target.value})}
        />
        <textarea
          placeholder="Content"
          value={note.content}
          onChange={(e) => setNote({...note, content: e.target.value})}
        />
        <select
          value={note.language}
          onChange={(e) => setNote({...note, language: e.target.value})}
        >
          <option value="en">English</option>
          <option value="bn">Bangla</option>
        </select>
        <button onClick={handleNoteSubmit}>Save Note</button>
      </div>

      <div>
        <h2>Create Calendar Event</h2>
        <input
          placeholder="Title"
          value={event.title}
          onChange={(e) => setEvent({...event, title: e.target.value})}
        />
        <textarea
          placeholder="Description"
          value={event.description}
          onChange={(e) => setEvent({...event, description: e.target.value})}
        />
        <input
          type="datetime-local"
          value={event.start_time}
          onChange={(e) => setEvent({...event, start_time: e.target.value})}
        />
        <input
          type="datetime-local"
          value={event.end_time}
          onChange={(e) => setEvent({...event, end_time: e.target.value})}
        />
        <button onClick={handleEventSubmit}>Create Event</button>
      </div>
    </div>
  );
}

export default App;