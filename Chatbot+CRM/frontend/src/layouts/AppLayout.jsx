import React from "react";
import { NavLink, Outlet } from "react-router-dom";
import ChatWidget from "../components/ChatWidget.jsx";

export default function AppLayout() {
  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Modular Platform</p>
          <h1>Chatbot + CRM Workspace</h1>
        </div>
        <nav className="nav-links">
          <NavLink to="/">General Chatbot</NavLink>
          <NavLink to="/crm">CRM Module</NavLink>
        </nav>
      </header>
      <main className="page">
        <Outlet />
        <ChatWidget />
      </main>
    </div>
  );
}
