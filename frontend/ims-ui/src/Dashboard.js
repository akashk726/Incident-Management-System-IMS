import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

/* ------------------ SEVERITY COLORS (for cards only) ------------------ */
const SEVERITY_STYLE = {
  P0: { bg: "#ffe5e5", color: "#d60000" },
  P1: { bg: "#fff3cd", color: "#856404" },
  P2: { bg: "#e7f3ff", color: "#0056b3" },
  P3: { bg: "#e6ffe6", color: "#2e7d32" },
  DEFAULT: { bg: "#eee", color: "#333" }
};

export default function Dashboard() {
  const [incidents, setIncidents] = useState([]);
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [severityFilter, setSeverityFilter] = useState("ALL");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  /* ------------------ FETCH ------------------ */
  const fetchData = async () => {
    try {
      setLoading(true);
      const res = await fetch("http://localhost:8000/incidents");
      const data = await res.json();
      setIncidents(Array.isArray(data) ? data : []);
    } catch {
      alert("Failed to fetch incidents");
    } finally {
      setLoading(false);
    }
  };

  /* ------------------ AUTO REFRESH ------------------ */
  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  /* ------------------ FILTER ------------------ */
  const filtered = useMemo(() => {
    return incidents.filter((i) => {
      return (
        (statusFilter === "ALL" || i.status === statusFilter) &&
        (severityFilter === "ALL" || i.severity === severityFilter) &&
        (i.component_id || "")
          .toLowerCase()
          .includes(search.toLowerCase())
      );
    });
  }, [incidents, statusFilter, severityFilter, search]);

  /* ------------------ KPI ------------------ */
  const total = incidents.length;
  const open = incidents.filter((i) => i.status === "OPEN").length;
  const closed = incidents.filter((i) => i.status === "CLOSED").length;

  return (
    <div style={page}>
      {/* HEADER */}
      <div style={header}>
        <h2 style={{ margin: 0 }}>IT Incident Dashboard</h2>
        <span style={{ color: "#888" }}>Real-time Monitoring</span>
      </div>

      {/* KPI */}
      <div style={kpiContainer}>
        <KPI label="Total" value={total} color="#2f6fed" />
        <KPI label="Open" value={open} color="#ff4d4f" />
        <KPI label="Closed" value={closed} color="#28a745" />
      </div>

      {/* FILTER BAR */}
      <div style={filtersBar}>
        <input
          type="text"
          placeholder="Search component..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={searchInput}
        />

        <select
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value)}
          style={dropdown}
        >
          <option value="ALL">All Priorities</option>
          <option value="P0">P0</option>
          <option value="P1">P1</option>
          <option value="P2">P2</option>
          <option value="P3">P3</option>
        </select>

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          style={dropdown}
        >
          <option value="ALL">All Statuses</option>
          <option value="OPEN">Open</option>
          <option value="CLOSED">Closed</option>
        </select>

        <button
          style={clearBtn}
          onClick={() => {
            setSearch("");
            setStatusFilter("ALL");
            setSeverityFilter("ALL");
          }}
        >
          Clear
        </button>
      </div>

      {/* LOADING */}
      {loading && <p style={{ textAlign: "center" }}>Loading...</p>}

      {/* EMPTY */}
      {!loading && filtered.length === 0 && (
        <p style={{ textAlign: "center", color: "#666" }}>
          No incidents found
        </p>
      )}

      {/* CARDS */}
      <div style={grid}>
        {filtered.map((i) => (
          <div
            key={i.id}
            style={card}

            /* 🔥 ADDED HOVER EFFECT (no change to existing logic) */
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-3px)";
              e.currentTarget.style.boxShadow =
                "0 6px 16px rgba(0,0,0,0.12)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "none";
              e.currentTarget.style.boxShadow =
                "0 4px 12px rgba(0,0,0,0.08)";
            }}
          >
            <div style={cardHeader}>
              <h3 style={{ margin: 0 }}>{i.component_id}</h3>

              {/* 🔥 UPDATED STATUS BADGE (cleaner) */}
              <span style={statusBadge(i.status)}>
                {i.status}
              </span>
            </div>

            <p style={subText}>Incident #{i.id}</p>

            <div style={badgeRow}>
              <span style={severityBadge(i.severity)}>
                {i.severity}
              </span>

              <span style={signalBadge}>
                Signals: {i.signal_count ?? 0}
              </span>
            </div>

            <p style={time}>
              {i.start_time
                ? new Date(i.start_time).toLocaleString()
                : "-"}
            </p>

            <Link to={`/incident/${i.id}`}>
              <button style={viewBtn}>View Details →</button>
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ------------------ KPI ------------------ */
function KPI({ label, value, color }) {
  return (
    <div style={{ ...kpi, borderTop: `4px solid ${color}` }}>
      <p style={{ margin: 0, color: "#666" }}>{label}</p>
      <h2 style={{ margin: 0 }}>{value}</h2>
    </div>
  );
}

/* ------------------ HELPERS ------------------ */
const severityBadge = (sev) => {
  const s = SEVERITY_STYLE[sev] || SEVERITY_STYLE.DEFAULT;
  return {
    padding: "4px 10px",
    borderRadius: "12px",
    fontSize: "12px",
    background: s.bg,
    color: s.color
  };
};

/* 🔥 UPDATED STATUS BADGE (improved version) */
const statusBadge = (status) => ({
  padding: "4px 10px",
  borderRadius: "12px",
  fontSize: "12px",
  background: status === "OPEN" ? "#e3f2fd" : "#e8f5e9",
  color: status === "OPEN" ? "#1976d2" : "#2e7d32"
});

/* ------------------ STYLES ------------------ */

/* 🔥 UPDATED PAGE BACKGROUND */
const page = {
  background: "#f5f7fa",
  minHeight: "100vh",
  padding: "25px",
  fontFamily: "Segoe UI"
};

const header = {
  display: "flex",
  justifyContent: "space-between",
  marginBottom: "20px"
};

const kpiContainer = {
  display: "flex",
  gap: "15px",
  marginBottom: "20px"
};

const kpi = {
  background: "#fff",
  padding: "12px",
  borderRadius: "10px",
  width: "120px",
  boxShadow: "0 2px 6px rgba(0,0,0,0.05)"
};

const filtersBar = {
  display: "flex",
  gap: "10px",
  marginBottom: "20px",
  alignItems: "center"
};

const searchInput = {
  padding: "8px",
  borderRadius: "8px",
  border: "1px solid #ccc",
  width: "220px"
};

const dropdown = {
  padding: "8px",
  borderRadius: "8px",
  border: "1px solid #ccc",
  color: "#000",
  background: "#fff"
};

const clearBtn = {
  padding: "8px 12px",
  borderRadius: "8px",
  border: "1px solid #ccc",
  cursor: "pointer"
};

const grid = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
  gap: "20px"
};

/* 🔥 UPDATED CARD STYLE */
const card = {
  background: "#ffffff",
  padding: "18px",
  borderRadius: "12px",
  boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
  transition: "0.2s ease"
};

const cardHeader = {
  display: "flex",
  justifyContent: "space-between"
};

const subText = {
  color: "#666"
};

const badgeRow = {
  display: "flex",
  justifyContent: "space-between",
  marginTop: "10px"
};

const signalBadge = {
  fontSize: "12px"
};

const time = {
  fontSize: "12px",
  color: "#888",
  marginTop: "10px"
};

const viewBtn = {
  marginTop: "12px",
  padding: "6px 10px",
  background: "#2f6fed",
  color: "#fff",
  border: "none",
  borderRadius: "6px",
  cursor: "pointer"
};