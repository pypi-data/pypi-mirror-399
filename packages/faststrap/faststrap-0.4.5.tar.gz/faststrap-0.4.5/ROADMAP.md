# FastStrap Roadmap – Updated December 2025

**Vision:** The most complete, Pythonic, zero-JS Bootstrap 5 component library for FastHTML — 100+ production-ready components built by the community, for the community.

---

## Current Status (v0.4.5 – February 2026)

**38 components live** – Phase 1 through 4B complete  
**230+ tests** – 80%+ coverage  
**Full HTMX + Bootstrap 5.3.3 support**  
**Zero custom JavaScript required**

### Completed Phases

| Phase | Components | Status | Released |
|-------|------------|--------|----------|
| 1–2 | 12 | ✅ Complete | Dec 2025 |
| 3 | +8 (Tabs, Dropdown, Input, Select, Breadcrumb, Pagination, Spinner, Progress) | ✅ Complete | Dec 2025 |
| 4A | +10 (Table, Accordion, Checkbox, Radio, Switch, Range, ListGroup, Collapse, InputGroup, FloatingLabel) | ✅ Complete | Jan 2026 |
| 4B | +8 (FileInput, Tooltip, Popover, Figure, ConfirmDialog, EmptyState, StatCard, Hero) | ✅ Complete | Feb 2026 |

**Total: 38 production-ready components**

---

## Phase 4A – Core Bootstrap Completion (v0.4.0 – Complete)

✅ **30 total components reached**

| Priority | Component | Status | Notes |
|----------|-----------|--------|-------|
| 1 | `Table` (+ THead, TBody, TRow, TCell) | ✅ Complete | Responsive, striped, hover, bordered |
| 2 | `Accordion` (+ AccordionItem) | ✅ Complete | Flush, always-open, icons |
| 3 | `Checkbox` | ✅ Complete | Standard, inline, validation |
| 4 | `Radio` | ✅ Complete | Standard, button style |
| 5 | `Switch` | ✅ Complete | Toggle variant of checkbox |
| 6 | `Range` | ✅ Complete | Slider with labels, steps |
| 7 | `ListGroup` (+ ListGroupItem) | ✅ Complete | Actionable, badges, flush |
| 8 | `Collapse` | ✅ Complete | Show/hide with data attributes |
| 9 | `InputGroup` | ✅ Complete | Prepend/append addons |
| 10 | `FloatingLabel` | ✅ Complete | Animated label inputs |

---

## Phase 4B – Enhanced Forms & Feedback (v0.4.5 – Complete)

✅ **38 total components reached**

### Components to Build

| Priority | Component | Status | Notes |
|----------|-----------|--------|-------|
| 1 | `FileInput` | ✅ Complete | Single/multiple, drag-drop preview |
| 2 | `Tooltip` | ✅ Complete | Bootstrap JS init pattern |
| 3 | `Popover` | ✅ Complete | Rich content overlays |
| 4 | `Figure` | ✅ Complete | Image + caption wrapper |
| 5 | `ConfirmDialog` | ✅ Complete | Modal preset for confirmations |
| 6 | `EmptyState` | ✅ Complete | Card + Icon + placeholder text |
| 7 | `StatCard` | ✅ Complete | Metric display card |
| 8 | `Hero` | ✅ Complete | Landing page hero section |

---

## Phase 5 – Layout & Navigation (v0.5.0 – Target Mar 2026)

**Goal:** SaaS-ready layout patterns  
**Target:** 50 total components

### Components to Build

| Priority | Component | Status | Owner | Notes |
|----------|-----------|--------|-------|-------|
| 1 | `Sidebar` | [ ] Open | — | Collapsible, responsive |
| 2 | `Footer` | [ ] Open | — | Standard layout component |
| 3 | `DashboardLayout` | [ ] Open | — | Sidebar + Topbar + Content |
| 4 | `Timeline` | [ ] Open | — | Activity/event timeline |
| 5 | `ProfileDropdown` | [ ] Open | — | Dropdown + Avatar pattern |
| 6 | `SearchBar` | [ ] Open | — | Input + suggestions |
| 7 | `FeatureCard` | [ ] Open | — | Icon + title + description |
| 8 | `PricingCard` | [ ] Open | — | Pricing table card |
| 9 | `Carousel` | [ ] Open | — | Slides, indicators, controls |
| 10 | `MegaMenu` | [ ] Open | — | Complex dropdown variant |
| 11 | `NotificationCenter` | [ ] Open | — | Toast stack + dropdown |
| 12 | `SectionDivider` | [ ] Open | — | Visual content separator |

---

## Phase 6 – Data & Advanced (v0.6.0 – Target May 2026) 

**Goal:** Advanced data display and interaction patterns  
**Target:** 60+ total components

### Components to Build

| Priority | Component | Status | Owner | Notes |
|----------|-----------|--------|-------|-------|
| 1 | `DataTable` | [ ] Open | — | Sorting, filtering, pagination |
| 2 | `TagInput` | [ ] Open | — | Dynamic badge/tag management |
| 3 | `FormWizard` / `Stepper` | [ ] Open | — | Multi-step form navigation |
| 4 | `FileUploader` | [ ] Open | — | Drag-drop with preview |
| 5 | `ChartContainer` | [ ] Open | — | Wrapper for chart libraries |
| 6 | `ChatBubble` | [ ] Open | — | Message bubble component |
| 7 | `ChatLayout` | [ ] Open | — | Full chat interface |
| 8 | `KanbanColumn` | [ ] Open | — | Drag-drop board columns |
| 9 | `ActivityFeed` | [ ] Open | — | Social-style activity list |
| 10 | `MediaGallery` | [ ] Open | — | Image/video grid layout |

---

## v1.0.0 – Production Release (Target Aug 2026)

**Goal:** Full Bootstrap parity + SaaS patterns + Documentation  
**Target:** 100+ components

### Milestones

- [ ] 100+ components
- [ ] 95%+ test coverage
- [ ] Full documentation website (MkDocs Material)
- [ ] Component playground / live demos
- [ ] 3-5 starter templates (Dashboard, Admin, E-commerce)
- [ ] Video tutorials
- [ ] Community contributions from 50+ developers

---

## Success Metrics

| Metric | v0.3.1 | v0.4.5 (Now) | v0.5.0 | v1.0.0 |
|--------|--------------|--------------|--------|--------|
| Components | 20 | 38 | 50 | 100+ |
| Tests | 219 | 230+ | 500+ | 800+ |
| Coverage | 80% | 85%+ | 90% | 95%+ |
| Contributors | 15+ | 25+ | 50+ | 100+ |

---

## How to Contribute

1. **Pick a component** from any Phase table above
2. **Comment on GitHub Issues** → "I'll build [Component]" → get assigned
3. **Use templates**: `src/faststrap/templates/component_template.py`
4. **Follow guides**: [BUILDING_COMPONENTS.md](BUILDING_COMPONENTS.md)
5. **Write tests**: 10-15 tests per component using `to_xml()`
6. **Submit PR** → merged in ≤48 hours

---

## Documentation Website (In Progress)

**Stack:** MkDocs Material + GitHub Pages

**Structure:**
- Getting Started (Installation, Quick Start)
- Component Reference (Forms, Display, Feedback, Navigation, Layout)
- Theming Guide (Built-in themes, Custom themes, Dark mode)
- HTMX Integration Guide
- API Reference

---

## Community Feedback

Tell us what you need most:
- [GitHub Discussions](https://github.com/Faststrap-org/Faststrap/discussions)
- Vote on issues with 👍
- [FastHTML Discord](https://discord.gg/qcXvcxMhdP) → #faststrap channel

Your votes directly influence what gets built next.

---

**Last Updated: February 2026**  
**Current Version: 0.4.5 (38 components live)**

**Let's build the definitive UI library for FastHTML — together.**