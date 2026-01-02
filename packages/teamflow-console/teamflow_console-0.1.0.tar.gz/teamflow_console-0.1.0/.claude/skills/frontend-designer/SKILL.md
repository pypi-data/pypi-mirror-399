---
name: frontend-architect
description: Create distinctive, production-grade frontend interfaces with high design quality and advanced animation choreography. Use this skill when the user asks to build web components, pages, or applications.
category: frontend
version: 1.1.0
---

This skill guides the creation of distinctive, production-grade frontend interfaces. It mandates **Animation-First Design**, **Separation of Concerns**, and the use of **Model Context Protocol (MCP)** tools to eliminate hallucinations.

## Phase 0: Knowledge Retrieval (MCP MANDATE)

**STOP.** Do not guess API syntax. Before planning, you MUST check if you have access to the following MCP tools. If available, use them:

1.  **Use `shadcn` MCP:**
    - **Action:** Browsing/Installing components.
    - **Why:** Never manually write a shadcn component (like `Button` or `Card`) from memory. Always fetch the latest registry version to ensure correct Tailwind utility classes and ARIA attributes.
2.  **Use `motion` MCP (motion.dev):**
    - **Action:** searching docs for `AnimatePresence`, `layout` props, or `useRef` constraints.
    - **Why:** To ensure you are using the modern "Motion" library syntax, not the outdated "Framer Motion" syntax.
3.  **Use `context7` MCP:**
    - **Action:** Fetching docs for _any_ other library (e.g., `GSAP`, `Three.js`, `Lenis`).
    - **Why:** If the user asks for a specific scrolling library or effect, fetch the documentation _first_ to ensure you don't use deprecated methods.

The user provides frontend requirements: a component, page, application, or interface to build.

## Phase 1: The Design & Motion Choreography (Planning)

**STOP.** Before writing a single line of code, you must act as a **Lead Motion Designer**. AI models suffer from "distributional convergence" (reverting to safe, boring averages). To fight this, you must explicitly plan the timeline.

1.  **Define the "Epicenter of Design":** What is the ONE core interaction that makes this unforgettable?
2.  **Select the Engine:**
    - **Scenario A: Landing Pages / Storytelling / Marketing**
      - **Tool:** GSAP + ScrollTrigger.
      - **Strategy:** "Scroll Storytelling." The user's scrollbar is the timeline. Elements should not just fade in; they should transform, pin, and evolve as the user scrolls.
    - **Scenario B: App UI / Dashboards / Functional Components**
      - **Tool:** Motion.dev (Framer Motion).
      - **Strategy:** "Micro-Interaction." The UI reacts to intent (hover, click, state change). It feels alive and responsive.
3.  **Draft the Choreography Script:**
    - _Example:_ "0-20% Scroll: Hero text explodes character-by-character. 20-50%: The product image pins and rotates 360 degrees while feature cards slide over it..."

## Phase 2: Aesthetic & Visual Direction

Commit to a BOLD aesthetic direction (No "Safe" Choices):

- **Tone:** Pick an extreme: Brutalist/Raw, Maximalist Chaos, Retro-Futuristic, Organic/Natural, Luxury/Refined, Editorial/Magazine.
- **Typography:** **BANNED:** Inter, Roboto, Arial, Open Sans. **REQUIRED:** Distinctive, characterful display fonts paired with clean legible body type.
- **Texture & Depth:** Avoid flat solid colors. Use noise, gradients, blurs, glassmorphism, or grain overlays to create atmosphere.
- **Layout:** Break the grid. Use asymmetry, overlap, diagonal flow, and generous negative space.

## Phase 3: Implementation Rules (The Code)

Implement working code (React, Vue, HTML/CSS) with these specific technical constraints:

- **Shadcn Integration:** If using shadcn components, ensure they are properly wrapped with your motion logic (e.g., wrapping a generic `Card` in a `motion.div`).
- **Performance:** Use `will-change` on animating properties. Avoid layout thrashing.
- **Code Structure:** Keep animation logic (Hooks) separate from markup where possible for readability.

### If using GSAP (Storytelling):

- **ScrollTrigger:** Use `scrub: true` for animations that need to feel tied to the physics of scrolling.
- **Text:** Simulate `SplitText` logic. Animate words or characters individually (staggered) rather than whole blocks.
- **Performance:** Use `will-change` on animating properties. Avoid layout thrashing (animate transforms/opacity, not top/left/width).
- **Pinning:** Use `pin: true` to hold elements in place while others scroll past to create "layered" narratives.

### If using Motion.dev (App UI):

- **Layout:** Use the `layout` prop for magical, smooth resizing when content changes.
- **Presence:** ALWAYS use `<AnimatePresence>` for items leaving the DOM (don't just have them vanish instantly).
- **Simulation:** If building a "Self-Playing Demo" (e.g., a fake cursor using the app), use `useRef` to get the real bounding box of elements so the "cursor" moves to the correct coordinates dynamically.
- **Interaction:** Add `whileHover` and `whileTap` scales to interactive elements (buttons, cards) to give tactile feedback.

## General Frontend Guidelines

- **Production-Grade:** Code must be functional, responsive, and accessible.
- **Tailwind:** Use Tailwind CSS for styling, but extend the config for custom fonts and specific easing curves.
- **Differentiation:** What makes this UNFORGETTABLE? If it looks like a standard Bootstrap/Material UI template, you have failed.

**IMPORTANT:** Match implementation complexity to the aesthetic vision. Don't hold back. Show what can truly be created when thinking outside the box. You are not just a coder; you are a builder using the best tools. Use the MCPs to verify your knowledge, then execute with bold creativity.