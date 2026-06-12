import React from "react";
import FeatureCard from "../components/FeatureCard.jsx";

const chatbotCapabilities = [
  {
    title: "Conversational Assistant",
    description: "Understand user questions, provide fast answers, and steer conversations smoothly.",
    items: [
      "Quick response generation",
      "Session-aware follow-ups",
      "Intent-sensitive replies"
    ]
  },
  {
    title: "Lead & CRM Guidance",
    description: "Help sales and marketing teams capture leads, recommend next steps, and generate follow-ups.",
    items: [
      "Lead qualification prompts",
      "Email and meeting suggestions",
      "CRM-aware action ideas"
    ]
  },
  {
    title: "Ticket & Support Flow",
    description: "Advise on support routing, ticket creation, and automated response handling.",
    items: [
      "Smart ticket suggestions",
      "FAQ response drafting",
      "Priority recommendations"
    ]
  },
  {
    title: "Predictive Insights",
    description: "Surface intelligence from CRM analytics, campaign performance, and customer signal predictions.",
    items: [
      "Conversion probability",
      "Lead status trends",
      "Response time estimates"
    ]
  }
];

const highlightCards = [
  {
    title: "Chat Interface",
    description: "Ask business questions directly and get immediate context-aware answers."
  },
  {
    title: "CRM Actions",
    description: "See how chatbot responses translate into lead, campaign, and support actions."
  },
  {
    title: "Easy Overview",
    description: "A single page that presents the platform capabilities in a clean, readable layout."
  }
];

export default function HomePage() {
  return (
    <div className="stack">
      <section className="hero">
        <p className="eyebrow">Unified Chatbot Experience</p>
        <h2>See the chatbot functions clearly, with every capability presented on one page.</h2>
        <p>
          This dashboard brings chatbot features, CRM guidance, support flows, and predictive insights together
          so visitors can understand the full value of your solution instantly.
        </p>
        <div className="hero-grid">
          {highlightCards.map((item) => (
            <article key={item.title} className="feature-summary">
              <h3>{item.title}</h3>
              <p>{item.description}</p>
            </article>
          ))}
        </div>
      </section>

      <section id="capabilities" className="grid">
        {chatbotCapabilities.map((feature) => (
          <FeatureCard key={feature.title} {...feature} />
        ))}
      </section>
    </div>
  );
}
