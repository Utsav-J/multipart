This is a nuanced and well-scoped question. Here's what the A2A spec, official docs, and community discussions reveal about where intent domains belong and why it matters for deterministic routing.

---

## What the A2A Spec Actually Says About Each Field

Starting from the normative source — the official proto definition — here is how each skill field is described:

**`id`** — "Unique identifier for the agent's skill." [A2a-protocol](https://a2a-protocol.org/v0.2.5/specification/) It is a stable machine-readable token, scoped to the agent.

**`tags`** — "A set of tags for the skill to enhance categorization/utilization," with the canonical example being `["cooking", "customer support", "billing"]`. [A2a-protocol](https://a2a-protocol.org/v0.3.0/specification/) The official tutorial documentation reinforces this, defining tags as "keywords for categorization and discovery." [A2a-protocol](https://a2a-protocol.org/latest/tutorials/python/3-agent-skills-and-card/) And the Codilime A2A breakdown explicitly calls out that tags are used "for user request routing." [CodiLime](https://codilime.com/blog/a2a-protocol-explained/)

**`description`** — "A human (or LLM) readable description of the skill details and behaviors." [A2a-protocol](https://a2a-protocol.org/v0.3.0/specification/) It is interpretive, not machine-matched.

**`examples`** — "Example prompts or scenarios that this skill can handle. Provides a hint to the client on how to use the skill." [A2a-protocol](https://a2a-protocol.org/v0.2.5/specification/) These are sample utterances, not routing keys.

---

## The Critical Nuance: Skills Are Not APIs

A key clarification from A2A community discussions is that skills are not APIs — they should not be treated as contract-based endpoints. Instead, they are descriptions of what the agent can do, often loosely defined. [GitHub](https://github.com/a2aproject/A2A/discussions/921)

This matters for a deterministic routing setup because the spec did not design `id` as an invocable endpoint key. In the A2A spec, each agent exposes a single JSON-RPC endpoint and communicates using a standardized set of methods. There are no custom method names; all interactions come through `message/send`, and the skill intent is implicitly embedded in the message/part field. [GitHub](https://github.com/a2aproject/A2A/discussions/547)

Furthermore, A2A interactions often begin with `message/send`, where a client sends a natural-language message and the server-side agent decides what to do. There is no universally enforced, first-class "invoke skill X" semantics in the core workflow. Many implementations solve this informally by embedding a `skillId` field inside a `DataPart`, but because this is not standardized, cross-vendor consistency and portability remain challenging. [CodiLime](https://codilime.com/blog/a2a-protocol-explained/)

---

## Where Intent Domains Should Live (For Deterministic Routing)

### 1. `tags` → Intent Domain Labels (Primary Home for Prefixes)

Tags are the field explicitly designed for this purpose. The spec's own canonical examples — `"customer support"`, `"billing"` — are intent domains, not capability verbs. In enterprise environments, curated registries allow clients to query and discover agents based on criteria like "skills" or "tags." [A2a-protocol](https://a2a-protocol.org/latest/topics/agent-discovery/) For a router, this means tags are the vocabulary a classifier indexes against when deciding which agent a query belongs to.

**Practical guidance:** Put all intent domain prefixes, synonyms, and sub-domain labels into `tags`. For example:

```json
{
  "id": "billing_support",
  "tags": ["billing", "billing.refund", "billing.invoice", "payment", "subscription"]
}
```

### 2. `id` → The Canonical Routing Key (The Router's Lookup Token)

While tags are for categorization and discovery, the `id` is the stable machine-readable identifier a routing table should anchor to. When an intent classifier produces an output, it should resolve to a `skill.id` → agent endpoint mapping. This is the cleanest deterministic contract because:

- Tags can have overlaps across agents (ambiguous for routing).
- `id` is guaranteed unique per agent — the spec defines it as the "unique identifier within this agent."

Community discussions around the multi-skill routing problem confirm that the client passing the skill name or ID as part of the A2A request, so the executor can map the intent to invoke different internal agents, is a recognized pattern — the routing logic is held internally, while the skill ID provides the reference point. [GitHub](https://github.com/a2aproject/A2A/issues/883)

**Practical guidance:** Make `id` reflect the intent domain in a canonical, stable, slug-like form (e.g., `billing_support`, `order_tracking`), and have the classifier's output class name match it.

### 3. `description` → Semantic Fallback (Not for Deterministic Routing)

Description is best left for human/LLM understanding of the skill. Scoping intent recognition and skill selection to a specific agent — rather than evaluating all skills globally — significantly reduces ambiguity and improves precision. [GitHub](https://github.com/a2aproject/A2A/discussions/921) In a deterministic classifier, routing should not rely on description-matching at runtime.

### 4. `examples` → LLM-Assisted Routing (Not Suited for Deterministic Routing)

Examples are useful when routing is LLM-based (semantic similarity matching), not when it is deterministic classifier-based.

---

## Recommended Pattern

```json
{
  "skills": [
    {
      "id": "billing.refund",
      "name": "Billing Refund Agent",
      "description": "Handles refund requests, disputed charges, and billing corrections.",
      "tags": ["billing", "billing.refund", "refund", "chargeback", "dispute"],
      "examples": ["I was charged twice", "I need a refund for my order"]
    }
  ]
}
```

The `id` becomes the routing table key. The `tags` become the classifier's matching vocabulary — carrying multiple prefixes, synonyms, and sub-intents. This provides both determinism (via `id`) and discoverability/indexability (via `tags`), which aligns with what the A2A spec designed each field to do.

---

## Sources

- **A2A Official Specification (proto normative definition):** https://a2a-protocol.org/v0.3.0/specification/ — defines the proto comments for all `AgentSkill` fields
- **A2A Official Tutorials — Agent Skills & Agent Card:** https://a2a-protocol.org/latest/tutorials/python/3-agent-skills-and-card/ — tags as "keywords for categorization and discovery"
- **A2A Official Docs — Agent Discovery:** https://a2a-protocol.org/latest/topics/agent-discovery/ — tags and skills as registry query criteria
- **Codilime A2A Protocol Explained:** https://codilime.com/blog/a2a-protocol-explained/ — explicitly identifies tags as being for "user request routing"
- **A2A GitHub Discussion #921 — Agent, Skill, and Intent Routing:** https://github.com/a2aproject/A2A/discussions/921 — community discussion on routing precision and skill scoping
- **A2A GitHub Issue #883 — Multi-Skill Agents:** https://github.com/a2aproject/A2A/issues/883 — community discussion on skill ID as internal routing token
- **A2A GitHub Discussion #547 — Requesting a Specific Skill:** https://github.com/a2aproject/A2A/discussions/547 — confirms skill intent is implicitly embedded in message payload, not routed by method
### Modify the System Prompt

Edit `agent.py` to customize:
- How answers are structured
- Number of follow-up questions (currently 3-5)
- What metadata to include

### Add Tools

You can add LangChain tools to the agent:

```python
from langchain_core.tools import tool

@tool
def search_knowledge_base(query: str) -> str:
    """Search the knowledge base."""
    ...

self.graph = create_react_agent(
    self.model,
    tools=[search_knowledge_base],  # Add your tools
    ...
)
```

## 🎓 Key Concepts

### Multi-Part Responses

A2A supports multiple content types in a single response:

- **TextPart**: Human-readable text
- **DataPart**: Structured JSON data
- **FilePart**: File attachments

You can combine these in a single `add_artifact` call.

### Why Use Multi-Part?

1. **Better UX**: Display text naturally while using data programmatically
2. **Structured Data**: Enable downstream processing without parsing text
3. **Rich Metadata**: Provide confidence scores, citations, follow-ups, etc.
4. **Separation of Concerns**: Keep presentation and data separate

## 📚 Related Examples

- **adk_expense_reimbursement**: Another multi-part response example
- **langgraph**: Basic LangGraph agent structure
- **helloworld**: Simplest A2A agent example

## 🐛 Troubleshooting

### Agent returns single-part response

Make sure you're using `add_artifact` with a list of `Part` objects:

```python
# ✅ Correct
parts = [Part(root=TextPart(...)), Part(root=DataPart(...))]
await updater.add_artifact(parts)

# ❌ Wrong - only sends text
await event_queue.enqueue_event(new_agent_text_message(...))
```

### Follow-up questions are generic

Improve your system prompt with more specific guidance about what makes good follow-up questions for your domain.

## 📄 License

Apache 2.0 - See the repository LICENSE file.
