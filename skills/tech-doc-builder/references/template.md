# Technical Documentation Template

Follow this structure exactly. Replace `3.X` with `3.1`, `3.2`, ... for each feature. Sections 1, 2, 3.X.1–3.X.4 were reconstructed to match the original template's spirit `[reconstructed]`; sections 3.X.5 onward are verbatim from the user's original template.

---

# <Project Name> — Technical Documentation

> **Document purpose:** Complete implementation specification. An AI coding agent reading this document must be able to implement the entire product without guessing.
> **Version / Date / Author** line.

## 1. Project Overview
- **Summary:** 2–4 sentences describing the product and its primary users.
- **Goals & non-goals:** bullet lists.
- **Feature index:** numbered table of all features documented in section 3 (Feature #, Name, One-line description, Priority).
- **Assumptions register:** table collecting every `[ASSUMPTION]` made in the document (ID, section, assumption, rationale) — filled in last.

## 2. Architecture & Tech Stack
- **Tech stack table:** Layer | Technology | Version | Purpose (frontend, backend, database, cache, queue, auth, hosting).
- **High-level architecture diagram:** Mermaid `flowchart` showing clients, gateway, services, data stores, external services.
- **Repository / project structure:** directory tree with one-line notes per top-level folder.
- **Naming conventions:** explicit statement (e.g., DB: snake_case; TypeScript: camelCase; components: PascalCase; API routes: kebab-case).
- **Authentication & authorization model:** mechanism (JWT/session/OAuth), token lifetimes, role list with permission matrix.

## 3. Features

Repeat the full 3.X block for every feature.

### 3.X <Feature Name>

#### 3.X.1 Feature Summary
- **User story:** As a <role>, I want <capability>, so that <benefit>.
- **Scope:** in-scope / out-of-scope bullets.
- **Acceptance criteria:** numbered, testable statements.

#### 3.X.2 UI / Frontend Specification
- **Screens/components:** component tree with exact component names (PascalCase) and file paths.
- **Component specs:** for each component — props (typed), state, events emitted.
- **User interactions:** step-by-step (click, input, navigation) with resulting behavior.
- **Frontend validation rules:** field-by-field (constraint, error message text).
- **Frontend state management:** store slices/atoms/contexts used, shape of state.
- **Loading / empty / error UI states:** what renders in each.

#### 3.X.3 API Contract
For every endpoint:
- Method, path, auth requirement, required role/permission.
- OpenAPI 3.1 YAML snippet or JSON Schema: request params/body, response body per status code (200/201/400/401/403/404/409/422/500), error envelope shape.
- Idempotency, pagination, sorting/filtering parameters where relevant.

#### 3.X.4 Backend Implementation
- **Business logic flow:** Step-by-step bullet list.
- **Service/domain layer:** class/function names, methods, parameters.
- **Middleware:** authentication, authorization (exact roles/permissions), validation, rate-limiting.
- **Database interactions:** Which tables/collections are read/written.
- **External service calls:** (email, payment, queue) — exactly when and with what payload.
- **Background jobs / queues:** Job name, trigger, payload, retry policy.

#### 3.X.5 Data Structures
- **Database schema** (table format):

| Table/Collection: `feature_items` | Type | Constraints | Indexes | Notes |
|----------------------------------|------|-------------|---------|-------|
| `id` | UUID | PK, NOT NULL | B-tree | |
| `title` | VARCHAR(100) | NOT NULL | | |
| `status` | ENUM('draft','published') | DEFAULT 'draft' | | |
| `created_by` | UUID (FK → users.id) | NOT NULL | B-tree | |

- Also provide the equivalent DDL (`CREATE TABLE ...`) or ORM model definition.
- **Relationships:** ER diagram in ASCII or Mermaid.
- **Data models** (TypeScript interfaces / Python dataclasses / Go structs) exactly as used in code.
- **Validation rules** (backend): libraries used, constraints, sanitization.

#### 3.X.6 Data Pipeline & Flow
- **Sequence diagram (Mermaid or text)** showing the full lifecycle for the main scenario, including frontend → API → service → DB → external services → response.
- **Event-driven flows:** which events are emitted, payload schema, consumers.
- **ETL / batch processing:** if applicable, describe schedule, source, transformation steps, target.
- **Caching strategy:** keys, TTL, invalidation triggers.

#### 3.X.7 Testing Specification
- **Unit tests:**
  - List test cases (Given-When-Then) for critical pure functions, validators, helpers.
- **Integration tests:**
  - API endpoint tests (with supertest/httptest), describe setup, mocked dependencies, assertions.
  - Database integration: test data seeding, transaction rollback.
- **E2E tests:** (Playwright/Cypress)
  - User journeys to automate.
  - Selectors, expected assertions.
- **Test data** (fixtures): minimal data set.
- **Mock requirements:** external services to mock and how (wiremock, nock, etc.).

#### 3.X.8 Error Handling & Edge Cases
- List every possible error state, how it is detected, and the exact response/message.
- Edge cases: empty input, extremely long input, concurrent requests, expired sessions, etc.

#### 3.X.9 Logging, Monitoring & Alerts
- What to log (level, message template, fields).
- Metrics to track (latency, error rate).
- Alerts threshold.

#### 3.X.10 Security Considerations
- Authentication / authorization checks.
- Data sanitization, SQL injection / XSS prevention.
- CSRF tokens, CORS policy.
- Rate limiting specific to this feature.

#### 3.X.11 Performance Considerations
- Expected load, latency budget.
- Optimisation techniques (pagination, query indexing, debouncing).
- Caching (if not covered in pipeline).

---

## 4. Cross-Feature Concerns
- **Shared components** (UI library).
- **Common backend services** (e.g., notification service).
- **Global state/context.**
- **Configuration / environment variables** table.

## 5. Deployment & Infrastructure Notes (brief)
- Environment differences (dev/staging/prod).
- CI/CD pipeline steps.
- Database migration strategy.

## 6. Glossary
Define all domain-specific terms.

---

# ⚙️ Writing Rules (Critical for AI Agent Consumption)
- **Be exhaustive, not verbose.** When in doubt, provide the schema or code snippet.
- **Use consistent naming** exactly matching the codebase (e.g., camelCase vs snake_case).
- **All API contracts** must be machine-parseable (JSON Schema / OpenAPI snippets).
- **All database schemas** must be presented as DDL or ORM model definitions.
- **State machines / flow** must be given in Mermaid (preferred) or a strict list of state transitions.
- **Testing descriptions** must use the `Given / When / Then` format and reference exact function/component names.
- **No placeholder text** — every section must be filled with concrete details derived from the project brief. If the brief lacks information, make reasonable architectural assumptions and clearly mark them with `[ASSUMPTION]`.
- The final document must be self-contained. When an AI reads it, it must be able to implement the entire feature without guessing.
