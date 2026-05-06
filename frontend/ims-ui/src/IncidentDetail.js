import { useParams, Link } from "react-router-dom";
import { useEffect, useState } from "react";

export default function IncidentDetail() {
  const { id } = useParams();
  const [incident, setIncident] = useState(null);
  const [form, setForm] = useState({});
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState("");

  // fetch incident
  useEffect(() => {
    fetch("http://localhost:8000/incidents")
      .then(res => res.json())
      .then(data => {
        const found = data.find(i => i.id === parseInt(id));
        setIncident(found);
      });
  }, [id]);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMsg("");

    try {
      const res = await fetch(`http://localhost:8000/close/${id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form)
      });

      const data = await res.json();
      setMsg(data.message || data.error);
    } catch {
      setMsg("Error closing incident");
    }

    setLoading(false);
  };

  if (!incident) return <p style={{ padding: "20px" }}>Loading...</p>;

  return (
    <div style={page}>
      
      {/* BACK */}
      <Link to="/" style={backBtn}>← Back</Link>

      <h2>Incident #{id}</h2>

      {/* INCIDENT INFO */}
      <div style={card}>
        <p><b>Component:</b> {incident.component_id}</p>
        <p><b>Status:</b> {incident.status}</p>
        <p><b>Severity:</b> {incident.severity}</p>
        <p><b>Signals:</b> {incident.signal_count}</p>
        <p><b>Start:</b> {new Date(incident.start_time).toLocaleString()}</p>
      </div>

      {/* CLOSE FORM */}
      {incident.status === "OPEN" && (
        <div style={card}>
          <h3>Close Incident (RCA)</h3>

          <form onSubmit={handleSubmit}>
            <input type="datetime-local" name="start" onChange={handleChange} required style={input} />
            <input type="datetime-local" name="end" onChange={handleChange} required style={input} />

            <input name="rootCause" placeholder="Root Cause" onChange={handleChange} required style={input} />
            <input name="fix" placeholder="Fix" onChange={handleChange} required style={input} />
            <input name="prevention" placeholder="Prevention" onChange={handleChange} required style={input} />

            <button disabled={loading} style={submitBtn}>
              {loading ? "Closing..." : "Close Incident"}
            </button>
          </form>

          {msg && <p style={{ marginTop: "10px" }}>{msg}</p>}
        </div>
      )}

      {/* CLOSED VIEW */}
      {incident.status === "CLOSED" && incident.rca && (
        <div style={card}>
          <h3>RCA Details</h3>
          <p><b>Root Cause:</b> {incident.rca.rootCause}</p>
          <p><b>Fix:</b> {incident.rca.fix}</p>
          <p><b>Prevention:</b> {incident.rca.prevention}</p>
          <p><b>MTTR:</b> {incident.mttr} sec</p>
        </div>
      )}
    </div>
  );
}

//
// 🎨 STYLES
//

const page = {
  padding: "20px",
  fontFamily: "Segoe UI",
  background: "#f4f6f8",
  minHeight: "100vh"
};

const card = {
  background: "#fff",
  padding: "15px",
  borderRadius: "10px",
  marginBottom: "15px",
  boxShadow: "0 2px 6px rgba(0,0,0,0.08)"
};

const input = {
  width: "100%",
  padding: "8px",
  marginBottom: "10px",
  borderRadius: "6px",
  border: "1px solid #ccc"
};

const submitBtn = {
  width: "100%",
  padding: "10px",
  background: "#2f6fed",
  color: "#fff",
  border: "none",
  borderRadius: "6px",
  cursor: "pointer"
};

const backBtn = {
  display: "inline-block",
  marginBottom: "10px",
  textDecoration: "none",
  color: "#2f6fed"
};