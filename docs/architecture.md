# Architecture Overview

## Principles

- The `core` module powers the general chatbot experience.
- The `crm` module is isolated and exposes its own routes, controllers, services, analytics, and automations.
- Shared concerns such as middleware and configuration live in `shared` and `config`.

## Runtime Boundaries

- General chatbot API: `/api/chat`
- CRM API: `/api/crm`
- Health endpoint: `/api/health`

## CRM Coverage

- Sales CRM: lead capture, qualification, scheduling, follow-up, upsell readiness
- Marketing CRM: segmentation, personalized campaigns, campaign automation, preference capture
- Support CRM: FAQ support, multilingual ticket creation, routing support history
- CRM Analytics: insight generation and predictive summaries
