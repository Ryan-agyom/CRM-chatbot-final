import React from "react";
import FeatureCard from "../components/FeatureCard.jsx";

const crmSections = [
  {
    title: "Sales CRM",
    description: "Lead generation, qualification, appointment scheduling, follow-ups, and upsell flows.",
    items: [
      "Capture name, email, phone, and requirements",
      "Score leads by budget, interest, company size, and timeline",
      "Book meetings and send reminders",
      "Trigger follow-ups and product recommendations"
    ]
  },
  {
    title: "Marketing CRM",
    description: "Personalized messaging and automation built from customer behavior.",
    items: [
      "Segment new, returning, inactive, and high-value customers",
      "Automate campaigns, coupons, greetings, and sale alerts",
      "Collect preferences, pain points, and feedback"
    ]
  },
  {
    title: "Support CRM",
    description: "24/7 support with multilingual answers, ticket creation, and guided resolution.",
    items: [
      "Answer FAQs for pricing, refunds, and order status",
      "Create and route support tickets",
      "Preserve conversation history for agents"
    ]
  },
  {
    title: "CRM Analytics",
    description: "Insights and predictive signals produced from CRM conversations.",
    items: [
      "Customer sentiment and complaint trends",
      "Popular product tracking",
      "Churn, conversion, and trend predictions"
    ]
  }
];

export default function CRMPage() {
  return (
    <div className="stack">
      <section className="hero crm-hero">
        <p className="eyebrow">Independent CRM Module</p>
        <h2>CRM-specific chatbot capabilities</h2>
        <p>
          This section is deployed as a separate backend module with its own services,
          controllers, repositories, automation rules, and analytics engine.
        </p>
      </section>
      <section className="grid">
        {crmSections.map((feature) => (
          <FeatureCard key={feature.title} {...feature} />
        ))}
      </section>
    </div>
  );
}
