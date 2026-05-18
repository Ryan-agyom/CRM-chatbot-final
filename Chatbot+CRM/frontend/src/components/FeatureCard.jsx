import React from "react";
export default function FeatureCard({ title, description, items = [] }) {
  return (
    <article className="card">
      <h3>{title}</h3>
      <p>{description}</p>
      <ul>
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </article>
  );
}
