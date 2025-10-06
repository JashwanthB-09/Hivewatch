
import React, { useState, useEffect } from "react";
import Sidebar from "./components/sidebar";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

// Fix Leaflet marker icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
});

// Dashboard Content
function DashboardContent({ attacks }) {
  return (
    <div style={{ padding: 20 }}>
      <h2>Dashboard</h2>

      {/* Summary Cards - ONLY on Dashboard */}
      <div style={{ display: "flex", gap: 20, marginBottom: 20 }}>
        <div style={{ flex: 1, padding: 10, border: "1px solid #ccc", borderRadius: 6, backgroundColor: "#f5f5f5" }}>
          <strong>Total Attacks:</strong> {attacks.length}
        </div>
        <div style={{ flex: 1, padding: 10, border: "1px solid #ccc", borderRadius: 6, backgroundColor: "#f5f5f5" }}>
          <strong>Honeypot Status:</strong> ✅
        </div>
        <div style={{ flex: 1, padding: 10, border: "1px solid #ccc", borderRadius: 6, backgroundColor: "#f5f5f5" }}>
          <strong>Live Attacks:</strong> {attacks.length}
        </div>
      </div>

      {/* Map + Live Attack Feed */}
      <div style={{ display: "flex", gap: 20 }}>
        <div style={{ width: "70%", height: "400px" }}>
          <MapContainer center={[20, 0]} zoom={2} style={{ width: "100%", height: "100%" }}>
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
            {attacks.map((a, i) =>
              a.geolocation ? (
                <Marker key={i} position={[a.geolocation.lat, a.geolocation.lon]}>
                  <Popup>
                    {a.source_ip} - {a.honeypot_type}
                  </Popup>
                </Marker>
              ) : null
            )}
          </MapContainer>
        </div>

        <div style={{ width: "30%", height: "400px", overflowY: "auto", border: "1px solid #ccc", padding: 10, borderRadius: 6, backgroundColor: "#f5f5f5" }}>
           <h3>Live Attacks</h3>
            <ul style={{ listStyle: "none", padding: 0 }}>
                 {attacks.map((a, i) => (
                     <li key={i} style={{ marginBottom: '12px', borderBottom: '1px solid #ddd', paddingBottom: '8px', fontSize: '14px' }}>
                     <strong>IP:</strong> {a.source_ip} <br />
                     <strong>Time:</strong> {new Date(a.timestamp).toLocaleString()} <br />
                     <strong>Location:</strong> {a.geolocation ? ${a.geolocation.city}, ${a.geolocation.country}` : 'Unknown Location'} <br />
                     <strong>Type:</strong> {a.honeypot_type}
                     </li>
           ))}
           </ul>
        </div>
      </div>
    </div>
  );
}

// Playbook Component
function Playbook() {
  const [playbook, setPlaybook] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/playbook")
      .then((res) => res.json())
      .then(setPlaybook)
      .catch(console.error);
  }, []);

  return (
    <div style={{ padding: 20 }}>
      <h2>Playbook</h2>
      {playbook.length > 0 ? (
        <ul>
          {playbook.map((p, i) => (
            <li key={i}>{p.action || JSON.stringify(p)}</li>
          ))}
        </ul>
      ) : (
        <p>No playbook data available.</p>
      )}
    </div>
  );
}

// Audit Component
function Audit() {
  const [audit, setAudit] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/audit")
      .then((res) => res.json())
      .then(setAudit)
      .catch(console.error);
  }, []);

  return (
    <div style={{ padding: 20 }}>
      <h2>Audit</h2>
      {audit.length > 0 ? (
        <ul>
          {audit.map((a, i) => (
            <li key={i}>{a.event || JSON.stringify(a)}</li>
          ))}
        </ul>
      ) : (
        <p>No audit data available.</p>
      )}
    </div>
  );
}

// Main App
export default function App() {
  const [activePage, setActivePage] = useState("Dashboard");
  const [attacks, setAttacks] = useState([]);

  // Fetch attacks globally for dashboard
  useEffect(() => {
    const fetchAttacks = () => {
      fetch("http://127.0.0.1:8000/api/attacks")
        .then((res) => res.json())
        .then(setAttacks)
        .catch(console.error);
    };
    fetchAttacks();
    const interval = setInterval(fetchAttacks, 2000);
    return () => clearInterval(interval);
  }, []);

  const renderPage = () => {
    switch (activePage) {
      case "Dashboard":
        return <DashboardContent attacks={attacks} />;
      case "Playbook":
        return <Playbook />;
      case "Audit":
        return <Audit />;
      default:
        return <div>Page Not Found</div>;
    }
  };

  return (
    <div className="flex">
      <Sidebar setActivePage={setActivePage} activePage={activePage} />
      <div className="flex-1">{renderPage()}</div>
    </div>
  );
}
