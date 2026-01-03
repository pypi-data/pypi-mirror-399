# Brand Guidelines

## Brand Overview
The Chat App project embodies the intersection of advanced AI technology and practical developer tools, emphasizing professionalism, reliability, and innovation in terminal-based LLM interfaces.

## Brand Personality

### Core Attributes
- **Professional**: Enterprise-ready, reliable, trustworthy
- **Innovative**: Cutting-edge AI integration, forward-thinking approach
- **Developer-Focused**: Built by developers, for developers
- **Minimalist**: Clean, efficient, no unnecessary complexity
- **Powerful**: Robust capabilities beneath simple interfaces

### Brand Voice
- **Tone**: Confident but approachable, technical but accessible
- **Style**: Clear, concise, action-oriented
- **Personality**: Expert mentor who respects the user's intelligence

## Visual Identity

### Logo System
```
Primary Logo: Chat App
- Font: Inter Bold, 24px
- Color: Lime Green (#a3e635)
- Usage: Main applications, headers, branding

Secondary Mark: CA
- Font: Inter Black, monospace styling
- Color: Terminal Green (#00ff88) on dark backgrounds
- Usage: Favicons, small applications, terminal prompts

Terminal Signature: chat_app$
- Font: JetBrains Mono, 16px
- Color: Terminal accent colors
- Usage: CLI interfaces, terminal documentation
```

### Color System

#### Primary Palette
```css
/* Brand Primary */
--brand-primary: #a3e635;
--brand-primary-dark: #84cc16;
--brand-primary-light: #bef264;

/* Terminal Theme - Neon Minimal Palette */
--terminal-bg: #1a1a1a;
--terminal-text: #e5e5e5;
--terminal-accent: #a3e635;  /* Lime green */
--terminal-info: #06b6d4;    /* Cyan */
--terminal-error: #ef4444;   /* Bright red */
--terminal-warning: #eab308; /* Gold */
--terminal-muted: #71717a;   /* Steel gray */

/* Documentation Theme */
--doc-bg: #ffffff;
--doc-text: #374151;
--doc-accent: #2563eb;
--doc-muted: #6b7280;
```

#### Extended Palette - Neon Minimal
```css
/* Success States (Lime Green) */
--success-green: #a3e635;
--success-green-light: #bef264;
--success-green-dark: #84cc16;

/* Info States (Cyan) */
--info-cyan: #06b6d4;
--info-cyan-light: #22d3ee;
--info-cyan-dark: #0891b2;

/* Warning States (Gold) */
--warning-gold: #eab308;
--warning-gold-light: #fde047;
--warning-gold-dark: #ca8a04;

/* Error States (Bright Red) */
--error-red: #ef4444;
--error-red-light: #f87171;
--error-red-dark: #dc2626;

/* Neutral Palette */
--gray-50: #f9fafb;
--gray-100: #f3f4f6;
--gray-200: #e5e7eb;
--gray-300: #d1d5db;
--gray-400: #9ca3af;
--gray-500: #71717a;    /* Steel - muted elements */
--gray-600: #52525b;
--gray-700: #3f3f46;
--gray-800: #27272a;
--gray-900: #18181b;
```

### Typography System

#### Font Hierarchy
```css
/* Primary Typeface - Interface */
.font-primary {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* Monospace - Code/Terminal */
.font-mono {
  font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', Monaco, monospace;
}

/* Display - Marketing/Presentations */
.font-display {
  font-family: 'Inter', system-ui, sans-serif;
  font-weight: 700;
  letter-spacing: -0.025em;
}
```

#### Scale and Weights
```css
/* Font Sizes */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */
--text-4xl: 2.25rem;   /* 36px */

/* Font Weights */
--font-light: 300;
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
--font-black: 900;
```

## Application Guidelines

### Terminal Interface Branding
```bash
# Welcome message branding
Welcome to Chat App v2.0.0
A professional LLM terminal interface

# Prompt styling
chat_app$ █

# Status indicators
[●] Processing...
[✓] Complete
[✗] Error
[!] Warning
```

### Documentation Branding
```markdown
# Header Treatment
Chat App | [Section Name]

# Footer Treatment
---
Chat App - Professional LLM Terminal Interface
Built with Claude Code | © 2025
```

### Presentation Materials
- **Slide Templates**: Clean, minimal design with brand colors
- **Headers**: Chat App logo + section title
- **Footers**: Consistent branding elements
- **Charts**: Brand color palette for data visualization

## Logo Usage

### Correct Usage
- Maintain minimum clear space (equal to logo height)
- Use approved color variations only
- Maintain aspect ratio when scaling
- Use on appropriate background contrasts

### Incorrect Usage
- Do not stretch or distort the logo
- Do not use unauthorized colors
- Do not place on low-contrast backgrounds
- Do not modify typography or spacing

### File Formats and Sizes
```
Logo Assets:
├── chat-app-logo.svg           # Vector primary
├── chat-app-logo-light.svg     # Light backgrounds
├── chat-app-logo-dark.svg      # Dark backgrounds
├── chat-app-icon.svg           # Icon only
├── chat-app-favicon.ico        # Favicon
└── social/
    ├── chat-app-og.png         # Open Graph (1200x630)
    ├── chat-app-twitter.png    # Twitter Card (1024x512)
    └── chat-app-linkedin.png   # LinkedIn (1200x627)
```

## Brand Applications

### Digital Presence
- **Website**: Professional, developer-focused design
- **GitHub**: Consistent README styling and project presentation
- **Documentation**: Clean, searchable, well-organized
- **Social Media**: Technical content with brand consistency

### Marketing Materials
- **Presentations**: Technical conference style
- **Case Studies**: Developer success stories
- **Tutorials**: Step-by-step with brand elements
- **Blog Posts**: Technical insights with brand voice

## Partnerships and Co-branding

### Claude Code Integration
- Acknowledge Claude Code partnership
- Use approved co-branding guidelines
- Maintain separate but complementary visual identity
- Follow Anthropic's brand guidelines for Claude references

### Third-party Integrations
- Respect partner brand guidelines
- Maintain Chat App brand prominence in our materials
- Use approved partnership badges and certifications
- Coordinate brand usage with legal requirements

## Brand Compliance

### Quality Standards
- All brand applications must meet accessibility standards
- Consistent color usage across all materials
- Typography choices support readability and professionalism
- Brand elements enhance rather than overwhelm content

### Review Process
- Brand usage review for major applications
- Approval process for co-branding opportunities
- Regular audit of brand compliance across materials
- Update guidelines based on brand evolution

### Brand Asset Management
- Centralized asset library with version control
- Approved templates for common applications
- Usage guidelines and examples
- Contact information for brand questions

## Measurement and Evolution

### Brand Health Metrics
- Brand recognition in developer community
- Consistent application across touchpoints
- User feedback on brand perception
- Competitive positioning assessment

### Evolution Guidelines
- Annual brand review and refinement
- User research to inform brand decisions
- Technology trend alignment
- Community feedback integration

---

*These brand guidelines ensure consistent, professional representation of the Chat App project across all touchpoints while supporting its mission as a premier AI-assisted development tool.*