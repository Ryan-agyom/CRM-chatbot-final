import React from "react";
import { Outlet } from "react-router-dom";
import ChatWidget from "../components/ChatWidget.jsx";

export default function AppLayout() {
  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Modular Platform</p>
          <h1>Chatbot + CRM Workspace</h1>
        </div>
        <nav className="nav-links" aria-label="Page navigation">
          <a href="#capabilities">Capabilities</a>
          <a href="#chat-widget">Live Chat</a>
        </nav>
      </header>
      <main className="page">
        <Outlet />
        <ChatWidget />
      </main>
      <footer className="site-footer">
        <p>All chatbot functionality is presented together so visitors can understand the platform at a glance.</p>
      </footer>
    </div>
  );
}
