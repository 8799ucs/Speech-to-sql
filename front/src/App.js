import "./App.css";
import SpeechRecognition, { useSpeechRecognition } from "react-speech-recognition";
import useClipboard from "react-use-clipboard";
import { useState, useEffect } from "react";
import axios from "axios";
import { onAuthStateChanged } from 'firebase/auth';
import { useNavigate } from 'react-router-dom';
import { auth} from './Firebase';

const databases = [
  { value: "sqlite", label: "SQLite" },
  { value: "mongodb", label: "MongoDB" },
  { value: "duckdb", label: "DuckDB" },
];

const App = () => {
  const [textToCopy, setTextToCopy] = useState("");
  const [isCopied, setCopied] = useClipboard(textToCopy, {
    successDuration: 1000,
  });
  const [data, setData] = useState([]);
  const [selectedDatabase, setSelectedDatabase] = useState("sqlite"); // Default database
  const navigate = useNavigate();
  const [user, setUser] = useState(null);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      if (currentUser) {
        console.log("Current user:", currentUser.email);
        const d=currentUser.email;
        setUser(d);
      } else {
        navigate('/');
      }
    });
    return unsubscribe;
  }, [navigate]);

  const sendTextToFlask = async (text) => {
    try {
      const response = await axios.post("http://localhost:5000/process_text", {
        text,
        database: selectedDatabase,
        user,
      });
      console.log(user);
      setData(response.data); // Update data state with the processed data
      console.log(response);
    } catch (error) {
      console.error(error);
    }
  };

  const startListening = () =>
    SpeechRecognition.startListening({ continuous: true, language: "en-IN" });
  const { transcript, browserSupportsSpeechRecognition } = useSpeechRecognition();

  useEffect(() => {
    setTextToCopy(transcript);
  }, [transcript, data]);

  if (!browserSupportsSpeechRecognition) {
    return <p>Your browser does not support speech recognition.</p>;
  }

  return (
    <>
      <div className="container">
        <h2>Speech to Text Converter</h2>
        <p>This page converts Speech to editable text.</p>

        <div className="database-selection">
          <label htmlFor="database">Select Database:</label>
          <select
            id="database"
            value={selectedDatabase}
            onChange={(e) => setSelectedDatabase(e.target.value)}
          >
            {databases.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
        <br />
        <div className="main-content">
          <textarea
            className="text-area"
            value={textToCopy}
            onChange={(e) => setTextToCopy(e.target.value)}
            placeholder="Speech will appear here..."
          />
        </div>
        <br />
        <div className="btn-style">
          <button onClick={setCopied}>
            {isCopied ? "Copied!" : "Copy to clipboard"}
          </button>
          <button onClick={startListening}>Start Listening</button>
          <button onClick={SpeechRecognition.stopListening}>Stop Listening</button>
          <button onClick={() => sendTextToFlask(textToCopy)}>Proceed</button>
        </div>
      </div>

      {/* Render Data as Table */}
      {data.length > 0 && (
        <div className="data-results">
          <h3>Processed Data from Flask:</h3>
          <table>
        <thead>
          <tr>
            {data[0].map((header, index) => (
              <th key={index}>{header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.slice(1).map((row, index) => (
            <tr key={index}>
              {row.map((cell,   
 cellIndex) => (
                <td key={cellIndex}>{cell}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
        </div>
      )}
    </>
  );
};

export default App;