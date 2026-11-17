# Legal Knowledge Graph & Mind Mapping Guide

## 1. Tool Landscape: Where Things Stand

### TheBrain (Free vs. Pro)
* **Strengths:** Unrivaled associative plex; fluid jumping between related thoughts; native C# speed.
* **Limitations:** 
  * The free tier restricts advanced search, attachments, and data export.
  * **Weak workflow visualization:** TheBrain organizes around a central focus thought with parent, child, and jump links. It cannot render sequential decision trees or step-by-step state diagrams (e.g., *“If $X \rightarrow$ file within 30 days $\rightarrow$ otherwise penalty $Y$”*).

### Why Neo4j Felt Overkill
* **Heavyweight:** Requires a persistent JVM server, complex configuration, and manual browser tooling.
* **Lack of Visual Mind Mapping:** Neo4j is a database backend, not a knowledge organizer. You have to write Cypher queries just to explore nodes unless you bolt on third-party visualizers like Bloom.

### The Modern Middle Ground: Kùzu
* If you want a modern, embeddable graph database without Neo4j's daemon overhead, **Kùzu** is the current standout (analogous to DuckDB or SQLite, but for property graphs). It runs in-process with C++, Python, and Rust APIs, supports openCypher, and requires zero server maintenance.

### The Visual Shift: Infinite Canvas (Obsidian Canvas / Heptabase)
* Over the past few years, the PKM (Personal Knowledge Management) space shifted toward **hybrid spatial canvases**.
* These allow you to mix:
  1. **Itemized hierarchies** (nested cards, articles, definitions).
  2. **Directional workflow paths** (labeled arrows, decision branches, timeline sequences).
* **Obsidian Canvas** uses an open, human-readable JSON specification (`.canvas`) that can be generated programmatically.

---

## 2. Modeling Legal Codes: The Dual-Layer Architecture

Legal documents cannot be modeled with a single graph pattern. They require two complementary layers:

```
[Legal Code]
  │
  ├── 1. Structural / Concept Layer (Taxonomy & Ontology)
  │     ├── Hierarchy: Title ➔ Chapter ➔ Article ➔ Paragraph
  │     └── Subjects: Defined terms, legal duties, rights, exceptions
  │
  └── 2. Procedural / Operational Layer (Workflow Automata)
        ├── Triggers: Occurrence of an event or deadline
        ├── Conditions: Pre-requisites (e.g., eligibility, thresholds)
        ├── Actions: Filings, notifications, obligations
        └── Outcomes: Approval, breach, sanction, remedy
```

### Layer 1: Structural Ontology (Itemized)
* **Node Types:** `Code`, `Chapter`, `Article`, `Subject/Concept`.
* **Edges:** `HAS_PART`, `DEFINES`, `REFERENCES`, `CROSS_APPLIES_TO`.
* **Example:** `Article 12` ➔ `DEFINES` ➔ `"Qualified Supplier"`.

### Layer 2: Workflow Automata (Directed Graph)
* **Node Types:** `State` (Start/Wait/Complete), `Condition` (Decision point), `Action` (Obligation/Filing).
* **Edges:** `TRANSITIONS_TO {guard: "Within 15 days"}`, `ON_FAILURE`, `ON_SUCCESS`.
* **Example:** `Filing Submitted` ➔ `[Under Review]` ➔ `If Approved` ➔ `License Issued` / `If Rejected` ➔ `File Appeal (15 days)`.

---

## 3. Recommended Workflow for Your Document

Rather than struggling with manual data entry:
1. **Source Document:** Provide the legal text (file, PDF, link, or snippet).
2. **Automated Parsing:** We extract both the **structural hierarchy** and the **procedural workflows**.
3. **Target Outputs:**
   * **TheBrain:** Generate a markdown outline or JSON importable directly into your local TheBrain database.
   * **Visual Canvas / SVG:** Generate responsive flowcharts and mind maps optimized for instant viewing.
   * **Embeddable Graph Data:** Export structured JSON or Kùzu/SQLite property tables for long-term programmatic querying.
