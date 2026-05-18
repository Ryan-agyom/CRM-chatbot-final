# Chatbot + CRM Monorepo

This project has two clear domains:

- `backend/src/core`: the general chatbot engine
- `backend/src/crm`: an independent CRM module for sales, marketing, support, and analytics

The frontend now talks to the backend chatbot route, and the backend can call the OpenAI Responses API when you provide an API key.

## Project Structure

```text
project-root/
|-- frontend/
|-- backend/
|-- docs/
|-- docker/
|-- .env
|-- .env.example
|-- docker-compose.yml
`-- README.md
```

## How The Chatbot Works

1. The frontend sends the user's message to `POST /api/chat`.
2. The backend keeps short session history in memory.
3. `backend/src/core/ai/provider.js` sends the prompt and recent history to OpenAI's Responses API.
4. The response text comes back to the frontend chat panel.

## OpenAI API Key Setup

This project expects your OpenAI key on the server side only. Do not place it in React code or browser-visible env vars.

### Where to create the key

1. Sign in to the OpenAI platform: `https://platform.openai.com/`
2. Open your API keys page: `https://platform.openai.com/api-keys`
3. Create a new secret key for the project you want to use.
4. Copy it once and store it safely.

Project keys and permissions are described in OpenAI's project/API key docs:
- Authentication overview: `https://developers.openai.com/api/reference/overview#authentication`
- Project key management: `https://platform.openai.com/docs/api-reference/project-api-keys/list`
- Project setup and permissions help: `https://help.openai.com/en/articles/9186755-managing-your-work-in-the-api-platform-with-projects`

### Put the key into this project

Copy `.env.example` to `.env` if needed, then set:

```env
PORT=5000
FRONTEND_URL=http://localhost:5173
VITE_API_URL=http://localhost:5000/api
OPENAI_API_KEY=sk-your-real-openai-key-here
OPENAI_MODEL=gpt-5.4-mini
OPENAI_API_BASE_URL=https://api.openai.com/v1
```

Notes:
- `OPENAI_API_KEY` is required for real replies.
- `OPENAI_MODEL` is configurable. This repo defaults to `gpt-5.4-mini` for a good latency/cost balance.
- The backend now loads the repo root `.env` automatically.

## Run The App

Install dependencies once:

```bash
cd backend
npm install
cd ../frontend
npm install
```

Start the backend:

```bash
cd backend
npm run dev
```

Start the frontend in a second terminal:

```bash
cd frontend
npm run dev
```

Open these URLs:

- Frontend: `http://localhost:5173`
- Backend health: `http://localhost:5000/api/health`

If the key is missing or invalid, the chat panel will now show the backend error message instead of silently failing.

## Test The Chatbot

After both servers are running:

1. Open `http://localhost:5173`
2. Type a message like `Explain what this chatbot project does`
3. Click `Send`
4. The reply should come from OpenAI through the backend

## How To Add Your Own Data

There are three common paths, and they solve different problems.

### 1. Prompting

Best when:
- You want to change tone, role, or response style
- You have a small amount of fixed guidance

Where to change it in this repo:
- `backend/src/core/prompts/basePrompts.js`

### 2. Retrieval / File Search

Best when:
- You want the chatbot to answer from documents, FAQs, PDFs, policies, or product knowledge
- Your data changes over time

This is usually the best first step instead of fine-tuning.

OpenAI's file search guide:
- `https://developers.openai.com/api/docs/guides/tools-file-search`

Recommended flow:
1. Gather your documents
2. Upload them to a vector store
3. Let the model search them at response time
4. Return grounded answers from your current data

### 3. Fine-Tuning

Best when:
- You need a very consistent style or format
- You have many high-quality input/output examples
- Prompting and retrieval are not enough

OpenAI fine-tuning guides:
- Supervised fine-tuning: `https://developers.openai.com/api/docs/guides/supervised-fine-tuning`
- Fine-tuning overview: `https://platform.openai.com/docs/guides/fine-tuning`

Important:
- Fine-tuning is not the usual first step for a business chatbot
- For most knowledge-based chatbots, retrieval is a better fit than "training on documents"

## Generate Synthetic CRM Data

This project now includes a built-in synthetic CRM seeder for test leads, campaigns, and support tickets.

### What it seeds

- Leads with names, emails, phone numbers, requirements, source, and a few qualification-style fields
- Campaigns with segment, message, and trigger
- Support tickets with issue, department, language, and a short conversation history

### Seed from the command line

Run this from `backend`:

```bash
npm run seed:crm
```

You can also pass counts:

```bash
node scripts/seed-crm-data.js 50 12 30
```

That means:
- `50` leads
- `12` campaigns
- `30` tickets

### Seed through the API

With the backend running, you can seed via:

```http
POST /api/crm/dev/seed
Content-Type: application/json
```

Example body:

```json
{
  "leads": 40,
  "campaigns": 8,
  "tickets": 20
}
```

### Inspect the seeded data

Use these endpoints:

- `GET /api/crm/leads`
- `GET /api/crm/campaigns`
- `GET /api/crm/support/tickets`
- `GET /api/crm/analytics/insights`

### Current storage model

Right now the seeded CRM data is integrated into this project's in-memory database layer:
- `backend/src/shared/database/inMemoryStore.js`
- `backend/src/crm/repositories/crm.repository.js`

That means:
- Data is available immediately to the backend while it is running
- Data resets when the backend process restarts

If you want persistent test data next, the clean next step is to move this repository layer to SQLite, PostgreSQL, or MongoDB and keep the same seeding service.

## Suggested Next Steps

1. Add a real document knowledge flow with file search or your own vector database.
2. Store sessions and CRM records in a real database instead of memory.
3. Add authentication and role-based access around CRM endpoints.
4. Add CRM-specific chatbot routes that use separate prompts and business rules.
