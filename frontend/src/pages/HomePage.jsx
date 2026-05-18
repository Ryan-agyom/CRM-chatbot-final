import React from "react";
import FeatureCard from "../components/FeatureCard.jsx";

const coreFeatures = [
  {
    title: "Conversation Engine",
    description: "Handles prompt routing, session management, and AI provider calls.",
    items: ["Session-aware conversations", "Reusable prompts", "Orchestration layer"]
  },
  {
    title: "Memory + Context",
    description: "Stores recent conversation state without coupling to CRM data.",
    items: ["Short-term memory", "Context builder", "Independent session store"]
  }
];

export default function HomePage() {
  return (
    <div className="stack">
      <section className="hero">
        <p className="eyebrow">Independent Core</p>
        <h2>General chatbot foundation</h2>
        <p>
          This area powers generic AI conversations, reusable prompts, and session handling.
          It does not depend on the CRM module.
        </p>
      </section>
      <section className="grid">
        {coreFeatures.map((feature) => (
          <FeatureCard key={feature.title} {...feature} />
        ))}
      </section>
    </div>
  );
}
