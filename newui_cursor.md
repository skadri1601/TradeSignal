# TradeSignal Landing Page - Detailed Implementation Guide

## Overview
This document provides comprehensive analysis and implementation details for creating a modern, glassmorphism-style landing page for TradeSignal, inspired by the Layzo design (https://layzo.webflow.io). The landing page will be publicly accessible without authentication, showcasing TradeSignal's features while keeping existing login/register pages unchanged.

## Design Analysis from Layzo Website

### Visual Design Elements

#### 1. Glassmorphism Navigation Bar
- **Effect**: Semi-transparent frosted glass with backdrop blur
- **Styling**:
  - Background: `rgba(255, 255, 255, 0.1)` or `rgba(30, 27, 75, 0.8)`
  - Backdrop filter: `blur(10px)` or `blur(20px)`
  - Border: `1px solid rgba(255, 255, 255, 0.2)`
  - Border radius: `12px` to `16px`
  - Box shadow: Subtle shadow for depth
- **Layout**: Full-width, fixed or sticky positioning
- **Elements**:
  - Logo on left (TradeSignal branding)
  - Navigation links in center: Home, Features, Pricing, About, Blog
  - "Sign In" button on right (links to `/login`)
- **Hover Effects**: 
  - Links: Subtle underline or glow
  - Buttons: Scale transform (1.05x) and brightness increase

#### 2. Hero Section
- **Background**:
  - Base: Deep purple gradient (`#1E1B4B` → `#312E81` → `#4C1D95`)
  - Center glow: Bright white/purple radial gradient creating luminous effect
  - Star particles: Small white dots scattered across dark areas (CSS or canvas animation)
  - Optional: Subtle animated particles floating
- **Typography**:
  - Main headline: Very large (72px-96px), bold, white, sans-serif
  - Subheading: Medium (24px-32px), lighter weight, white/gray
  - Tagline pill: Small pill-shaped badge with icon + text
- **Layout**:
  - Full viewport height or large section
  - Headline positioned left-center
  - CTA buttons positioned right-bottom
  - Content centered vertically with padding

#### 3. Color Palette
```css
/* Primary Colors */
--purple-900: #1E1B4B;  /* Darkest background */
--purple-800: #312E81;  /* Dark background */
--purple-700: #4C1D95;  /* Medium dark */
--purple-600: #5B21B6;  /* Medium */
--purple-500: #7C3AED;  /* Primary purple */
--purple-400: #A78BFA;  /* Light purple */
--purple-300: #C4B5FD;  /* Lighter purple */
--purple-200: #DDD6FE;  /* Very light purple */

/* Accent Colors */
--blue-500: #3B82F6;    /* Accent blue */
--white: #FFFFFF;        /* Text on dark */
--gray-300: #D1D5DB;    /* Light text */
--gray-600: #4B5563;    /* Medium text */

/* Glassmorphism */
--glass-bg: rgba(255, 255, 255, 0.1);
--glass-border: rgba(255, 255, 255, 0.2);
--glass-dark-bg: rgba(30, 27, 75, 0.8);
```

#### 4. Typography
- **Font Family**: Modern sans-serif (Inter, Poppins, or system fonts)
- **Headings**:
  - H1: 72px-96px, font-weight: 700-800, line-height: 1.1
  - H2: 48px-64px, font-weight: 700, line-height: 1.2
  - H3: 32px-40px, font-weight: 600, line-height: 1.3
- **Body**: 16px-18px, font-weight: 400, line-height: 1.6
- **Small text**: 14px, font-weight: 400

#### 5. Spacing & Layout
- **Container**: Max-width 1280px, centered, padding 24px-48px
- **Section spacing**: 80px-120px between major sections
- **Card padding**: 24px-32px
- **Border radius**: 12px-16px for cards, 8px-12px for buttons

### Animation Patterns

#### 1. Scroll Animations
- **Fade in on scroll**: Elements fade in as they enter viewport
- **Parallax**: Background elements move slower than foreground
- **Stagger**: Cards animate in sequence (50ms-100ms delay between each)

#### 2. Hover Effects
- **Cards**: 
  - Scale: `transform: scale(1.02)`
  - Shadow increase
  - Border glow
- **Buttons**:
  - Scale: `transform: scale(1.05)`
  - Background brightness increase
  - Smooth transition (200ms-300ms)
- **Links**: Underline animation or color change

#### 3. Background Animations
- **Star particles**: Subtle floating/moving animation
- **Gradient glow**: Pulsing or slow movement
- **Particle system**: Optional canvas-based particle animation

## Component Structure

### 1. LandingPage.tsx (Main Component)
```typescript
// Structure:
<LandingPage>
  <GlassmorphicNav />
  <HeroSection />
  <WhyChooseUsSection />
  <FeaturesGridSection />
  <HowItWorksSection /> (optional)
  <TestimonialsSection /> (optional)
  <CTASection />
  <LandingFooter />
</LandingPage>
```

### 2. GlassmorphicNav Component
**Props**: None (uses React Router for navigation)
**Features**:
- Fixed/sticky positioning
- Glassmorphism styling
- Responsive mobile menu
- Active link highlighting
- Smooth scroll to sections

**Implementation Details**:
```tsx
// Key CSS classes needed:
- backdrop-blur-lg or backdrop-blur-xl
- bg-white/10 or bg-purple-900/80
- border border-white/20
- rounded-xl or rounded-2xl
- shadow-lg
```

### 3. HeroSection Component
**Props**: None
**Features**:
- Full viewport or large section
- Animated background with particles
- Large headline
- Subheading
- Tagline pill
- Two CTA buttons (Get Started, View Features)
- Responsive typography

**Background Implementation**:
```tsx
// Option 1: CSS Gradient + Pseudo-elements for stars
<div className="relative overflow-hidden">
  <div className="absolute inset-0 bg-gradient-to-br from-purple-900 via-purple-800 to-purple-900" />
  <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_rgba(255,255,255,0.3)_0%,_transparent_70%)]" />
  {/* Star particles using CSS or canvas */}
</div>

// Option 2: Canvas for animated particles (more advanced)
```

### 4. FeatureCard Component
**Props**:
- `icon`: React component or icon name
- `title`: string
- `description`: string
- `highlight`: boolean (optional)

**Styling**:
- Glassmorphism effect
- Rounded corners
- Hover animations
- Icon with colored background circle

### 5. FeatureGrid Component
**Props**:
- `features`: Array of feature objects
- `columns`: 2 or 3 (responsive)

**Layout**: CSS Grid with responsive breakpoints

### 6. LandingFooter Component
**Props**: None
**Features**:
- Multi-column layout
- Navigation links
- Social media icons
- Copyright information
- Dark background (not glassmorphism)

## Technical Implementation

### Tailwind Configuration Updates

Add to `tailwind.config.js`:

```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        purple: {
          900: '#1E1B4B',
          800: '#312E81',
          700: '#4C1D95',
          // ... standard Tailwind purples
        },
      },
      backdropBlur: {
        xs: '2px',
      },
      animation: {
        'fade-in': 'fadeIn 0.6s ease-in-out',
        'slide-up': 'slideUp 0.6s ease-out',
        'float': 'float 3s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
      },
    },
  },
}
```

### CSS Utilities for Glassmorphism

Add to `index.css` or create utility classes:

```css
.glass {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.glass-dark {
  background: rgba(30, 27, 75, 0.8);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.glass-hover:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: scale(1.02);
  transition: all 0.3s ease;
}
```

### React Router Integration

**Current State**: 
- `/` → Protected Dashboard (requires auth)
- `/login` → LoginPage (no layout)
- `/register` → RegisterPage (no layout)

**Required Changes**:
- `/` → LandingPage (public, no layout)
- `/dashboard` → Dashboard (protected, with layout)
- `/login` → LoginPage (unchanged)
- `/register` → RegisterPage (unchanged)

**Implementation in App.tsx**:
```tsx
<Routes>
  {/* Auth routes - NO LAYOUT */}
  <Route path="/login" element={<LoginPage />} />
  <Route path="/register" element={<RegisterPage />} />
  
  {/* Landing page - NO LAYOUT */}
  <Route path="/" element={<LandingPage />} />
  
  {/* All other routes - WITH LAYOUT */}
  <Route path="/*" element={
    <Layout>
      <Routes>
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        {/* ... other protected routes */}
      </Routes>
    </Layout>
  } />
</Routes>
```

## Feature Content for TradeSignal

### Hero Section Content
- **Headline**: "Real-Time Insider Trading Intelligence"
- **Subheading**: "Track SEC Form 4 filings, congressional trades, and market-moving transactions with AI-powered insights that help you make informed investment decisions."
- **Tagline**: "AI-Powered Market Insights"
- **CTA Primary**: "Get Started" → `/register`
- **CTA Secondary**: "View Features" → Scroll to features section

### Why Choose TradeSignal Section
**Title**: "Why Choose TradeSignal"

**Three Feature Cards**:

1. **Real-Time SEC Data**
   - Icon: Database or TrendingUp
   - Title: "Live Insider Trading Data"
   - Description: "Track 3,761+ real insider trades from SEC Form 4 filings across 164 companies. All data sourced directly from SEC EDGAR database with 100% accuracy."

2. **AI-Powered Insights**
   - Icon: Brain or Sparkles
   - Title: "Intelligent Market Analysis"
   - Description: "Get AI-powered analysis of trades and market patterns. Understand why insiders are buying or selling with natural language summaries."

3. **Congressional Transparency**
   - Icon: Building2 or Shield
   - Title: "Political Trading Tracking"
   - Description: "Monitor congressional stock transactions and political trading activity. Stay informed about market-moving political decisions."

### Features Grid Section
**Title**: "Everything You Need to Track Insider Activity"

**Four Feature Cards (2x2 Grid)**:

1. **Insider Trading Dashboard**
   - Description: "Comprehensive dashboard showing recent trades, trending companies, and market activity at a glance."

2. **Custom Alerts & Notifications**
   - Description: "Set up custom alerts for specific companies, insiders, or trade types. Get notified instantly via push notifications."

3. **Company & Insider Profiles**
   - Description: "Detailed profiles for companies and insiders with historical trading data, stock charts, and related news."

4. **Market Intelligence**
   - Description: "Live market indices, sector performance, Fed calendar, and curated financial news all in one place."

## Responsive Design Breakpoints

### Mobile (< 640px)
- Navigation: Hamburger menu
- Hero: Full-width, stacked layout
- Typography: Smaller sizes (H1: 36px-48px)
- Cards: Single column
- Padding: 16px-24px

### Tablet (640px - 1024px)
- Navigation: Horizontal with fewer items
- Hero: Two-column layout possible
- Cards: 2 columns
- Padding: 24px-32px

### Desktop (> 1024px)
- Navigation: Full horizontal
- Hero: Multi-column layout
- Cards: 3-4 columns
- Padding: 32px-48px

## Animation Implementation

### Using Framer Motion (Recommended)
```tsx
import { motion } from 'framer-motion';

// Fade in on scroll
<motion.div
  initial={{ opacity: 0, y: 20 }}
  whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true }}
  transition={{ duration: 0.6 }}
>
  {/* Content */}
</motion.div>

// Stagger children
<motion.div
  initial="hidden"
  whileInView="visible"
  viewport={{ once: true }}
  variants={{
    visible: {
      transition: {
        staggerChildren: 0.1
      }
    }
  }}
>
  {features.map((feature, i) => (
    <motion.div
      key={i}
      variants={{
        hidden: { opacity: 0, y: 20 },
        visible: { opacity: 1, y: 0 }
      }}
    >
      <FeatureCard {...feature} />
    </motion.div>
  ))}
</motion.div>
```

### Using CSS Only
```css
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-in-up {
  animation: fadeInUp 0.6s ease-out;
}

/* Intersection Observer for scroll animations */
```

## Performance Considerations

1. **Lazy Loading**: Use React.lazy() for LandingPage component
2. **Image Optimization**: Optimize any background images
3. **Animation Performance**: Use `transform` and `opacity` for animations (GPU accelerated)
4. **Particle System**: Limit particle count on mobile devices
5. **Code Splitting**: Separate landing page bundle from main app

## Accessibility

1. **Semantic HTML**: Use proper heading hierarchy (h1, h2, h3)
2. **ARIA Labels**: Add labels for interactive elements
3. **Keyboard Navigation**: Ensure all interactive elements are keyboard accessible
4. **Color Contrast**: Maintain WCAG AA contrast ratios (4.5:1 for text)
5. **Focus Indicators**: Visible focus states for keyboard navigation
6. **Alt Text**: Descriptive alt text for images

## Testing Checklist

- [ ] Landing page loads at `/` without authentication
- [ ] Navigation links work correctly
- [ ] "Sign In" button links to `/login`
- [ ] "Get Started" button links to `/register`
- [ ] Responsive design works on mobile/tablet/desktop
- [ ] Animations are smooth and performant
- [ ] Existing login/register pages unchanged
- [ ] Dashboard accessible at `/dashboard` for authenticated users
- [ ] Glassmorphism effects work in all browsers
- [ ] Scroll animations trigger correctly
- [ ] Hover effects work on all interactive elements
- [ ] Accessibility standards met

## Browser Compatibility

- **Modern Browsers**: Full support (Chrome, Firefox, Safari, Edge)
- **Backdrop Filter**: May need fallback for older browsers
  ```css
  /* Fallback for browsers without backdrop-filter */
  @supports not (backdrop-filter: blur(10px)) {
    .glass {
      background: rgba(30, 27, 75, 0.95);
    }
  }
  ```

## File Structure

```
frontend/src/
├── pages/
│   └── LandingPage.tsx          # Main landing page component
├── components/
│   └── landing/
│       ├── GlassmorphicNav.tsx  # Navigation bar
│       ├── HeroSection.tsx      # Hero section
│       ├── FeatureCard.tsx     # Reusable feature card
│       ├── FeatureGrid.tsx     # Feature grid layout
│       ├── WhyChooseUs.tsx     # Why Choose Us section
│       ├── CTASection.tsx      # Call-to-action section
│       └── LandingFooter.tsx   # Footer component
└── App.tsx                      # Updated routing
```

## Implementation Order

1. **Setup**: Update Tailwind config, add CSS utilities
2. **Navigation**: Create GlassmorphicNav component
3. **Hero**: Create HeroSection with background and animations
4. **Features**: Create FeatureCard and FeatureGrid components
5. **Sections**: Build WhyChooseUs and other sections
6. **Footer**: Create LandingFooter component
7. **Integration**: Update App.tsx routing
8. **Polish**: Add animations, responsive design, testing

## Key Dependencies

- **React Router**: Already installed (for navigation)
- **Framer Motion**: Optional but recommended for animations
  ```bash
  npm install framer-motion
  ```
- **Lucide React**: Already used (for icons)
- **Tailwind CSS**: Already configured

## Notes for Implementation

1. **Keep it Simple**: Start with basic structure, add animations later
2. **Mobile First**: Design for mobile, enhance for desktop
3. **Performance**: Monitor bundle size and animation performance
4. **Consistency**: Match existing TradeSignal design language where possible
5. **Content**: All content should be TradeSignal-specific, not generic
6. **Testing**: Test on multiple devices and browsers
7. **Accessibility**: Don't skip accessibility features

## Questions to Resolve

1. Should authenticated users visiting `/` be redirected to `/dashboard` or see landing page?
2. Do we need a "Skip to Dashboard" link for logged-in users on landing page?
3. Should the landing page have a different header/footer than the main app?
4. Do we want to add analytics tracking to landing page?
5. Should we A/B test different headlines or CTAs?

## Detailed Analysis: Layzo About Us Page

This section provides a comprehensive analysis of the Layzo About Us page (https://layzo.webflow.io/about) to understand the design patterns, layout structure, and visual elements that can be adapted for TradeSignal's About page or similar content sections.

### Page Structure Overview

The About Us page consists of the following main sections:
1. **Hero/Introduction Section** - Large heading with company philosophy
2. **Logo Showcase Section** - Visual display of company logos/branding
3. **Value Proposition Section** - Three numbered value cards
4. **Awards & Recognition Section** - Achievement showcase with dates
5. **Meet Our Teams Section** - Team member profiles in cards
6. **Footer Section** - Navigation, links, and animated marquee

### Section-by-Section Analysis

#### 1. Hero/Introduction Section

**Layout:**
- Full-width section with dark, atmospheric background
- Large "About Us" heading (H2, white text)
- Multi-paragraph introduction text
- Clean, centered or left-aligned text layout

**Content Structure:**
```
## About Us

[Introductory paragraph about company philosophy]
- "At Layzo, we believe great design is more than visuals—it's an experience."
- "We're a multidisciplinary design studio driven by curiosity, creativity, and a passion for solving real problems with bold ideas."

[Supporting paragraphs]
- "We focus on crafting meaningful experiences through unique strategy, design, and storytelling."
- "Our approach helps ambitious businesses forge strong connections."
```

**Design Elements:**
- Dark background (similar to hero section - purple/black gradient)
- Large, bold typography for heading
- White/gray text for body content
- Generous spacing between paragraphs
- Possibly includes subtle background graphics or lighting effects

**Typography:**
- Heading: Large (48px-64px), bold, white
- Body: Medium (16px-18px), regular weight, white/gray
- Line height: 1.6-1.8 for readability

#### 2. Logo Showcase Section

**Layout:**
- Grid of logo images (appears to be 10 logos based on content)
- Possibly in a carousel, grid, or marquee format
- Each logo labeled as "About Logo" (placeholder)

**Design Pattern:**
- Clean white or light background
- Logos arranged in a grid (2x5, 5x2, or responsive grid)
- Equal spacing between logos
- Possibly grayscale logos that become colored on hover
- Smooth transitions between logos if carousel

**Implementation Notes:**
- Use CSS Grid or Flexbox for layout
- Responsive: 2-3 columns on desktop, 1-2 on tablet, 1 on mobile
- Hover effects: Scale or color transition
- Optional: Auto-scrolling carousel or manual navigation

#### 3. Value Proposition Section (Numbered Cards)

**Layout:**
- Three cards arranged horizontally (desktop) or stacked (mobile)
- Each card numbered: (01), (02), (03)
- Each card has a "Value Image" placeholder

**Card Structure:**
```
(01)
### We Provide High Quality Service.
Every project is crafted with precision, creativity, and a commitment to excellence.

(02)
### It's About Crafting Experiences
Every project is crafted with precision, creativity, and a commitment to excellence.

(03)
### Partnerships Are What We Do
Every project is crafted with precision, creativity, and a commitment to excellence.
```

**Design Elements:**
- Glassmorphism or soft card design
- Rounded corners (12px-16px)
- Numbered labels in large, bold font
- H3 headings for titles
- Body text below title
- Visual image/icon for each value
- Subtle hover effects

**Styling:**
- Background: Semi-transparent or soft gradient
- Border: Subtle border or shadow
- Spacing: Generous padding (24px-32px)
- Typography: Bold headings, regular body text

#### 4. Awards & Recognition Section

**Layout:**
- Section heading: "Awards & Recognition"
- Introductory paragraph
- Grid of award cards (4 awards visible)

**Award Card Structure:**
Each award card contains:
- Award icon/image
- Award title (H3)
- Description text
- Date (formatted as "Month DD, YYYY")

**Example Awards:**
1. **Top Designer Feature**
   - "Highlighted for outstanding visual storytelling and design craft."
   - Date: "Jan 30, 2025"

2. **Great Honorable Mention**
   - "Recognized for innovation and creativity in web design."
   - Date: "Feb 24, 2025"

3. **Design Excellence Award**
   - "Honored for crafting impactful brand identities and digital experiences."
   - Date: "Mar 06, 2025"

4. **Best Community Awards**
   - "Honored for advancing the Webflow ecosystem with creativity and impact."
   - Date: "Aug 15, 2025"

**Design Elements:**
- Cards with icons on left or top
- Clean, readable typography
- Date formatting: Short month, day, year
- Possibly trophy or badge icons
- Grid layout: 2x2 on desktop, 2x1 on tablet, 1x1 on mobile

**Styling:**
- Light or dark background (depending on page theme)
- Card-based layout with subtle shadows
- Icon + text combination
- Consistent spacing and alignment

#### 5. Meet Our Teams Section

**Layout:**
- Section heading: "Meet our Teams"
- Introductory paragraph (same as Awards section)
- Grid of team member cards (4 members)
- CTA button below cards

**Team Member Card Structure:**
Each card contains:
- Profile image (circular, top-left position)
- Name (bold, large font)
- Title/Role (smaller, lighter font)
- Social media icons (3 icons per member)

**Team Members:**
1. **Ralph Edwards** - Web Designer
2. **Esther Howard** - CEO at StoryPixel
3. **Ronald Richards** - Marketing Coordinator
4. **Darlene Robertson** - President of Sales

**Card Design (Detailed Analysis):**

**Visual Style:**
- Rounded rectangles with significant border-radius (20px-30px)
- Soft, pastel gradient backgrounds:
  - Card 1: Light blue to purple-blue gradient
  - Card 2: Soft pink to light purple gradient
  - Card 3: Light yellow to warm orange gradient
  - Card 4: Light blue to purple-blue gradient
- Subtle grid or dot pattern overlay on gradients
- Glassmorphism/soft UI aesthetic

**Layout within Card:**
- Profile image: Circular, positioned top-left, slightly overlapping card edge
- Name: Large, bold, black text below image
- Title: Smaller, gray text below name
- Social icons: Small icons (likely LinkedIn, Twitter, etc.) positioned near name/title

**Spacing:**
- Horizontal spacing between cards: 24px-32px
- Vertical spacing from section top: 48px-64px
- Vertical spacing to CTA button: 48px-64px
- Card padding: 24px-32px

**Typography:**
- Names: 18px-24px, font-weight: 600-700, black
- Titles: 14px-16px, font-weight: 400-500, gray
- Font family: Modern sans-serif (Inter, Poppins)

**Call-to-Action Button:**
- Text: "Apply Now To Join Our Team"
- Icon: Right-pointing arrow (→)
- Style: Rounded rectangle, medium purple background, white text
- Position: Centered below team cards
- Hover: Scale transform (1.05x), brightness increase

**Responsive Behavior:**
- Desktop: 4 cards in a row
- Tablet: 2x2 grid
- Mobile: 1 column (stacked)

**Animation Patterns:**
- Cards fade in on scroll (staggered animation)
- Hover effects: Scale (1.02x), shadow increase
- Button hover: Scale (1.05x), color transition

#### 6. Footer Section

**Layout:**
- Multi-column layout
- Dark background (not glassmorphism)
- Footer logo and tagline at top
- Navigation links organized in columns
- Social media icons
- Copyright information
- Animated marquee section

**Column Structure:**
1. **Company Column:**
   - Home
   - About
   - Blog
   - Work

2. **Resources Column:**
   - Blog Details
   - Work Details
   - Contact Us

3. **Others Column:**
   - Style Guide
   - License
   - Changelog

4. **Utility Pages Column:**
   - Privacy Policy
   - Terms of Service

**Special Elements:**
- **Tagline**: "Together, we turn your vision into reality."
- **Form Messages**: Success/error messages for contact forms
- **Social Icons**: Multiple social media platform icons (8 icons visible)
- **Animated Marquee**: "We are available" text scrolling horizontally
  - Repeats multiple times
  - Smooth, continuous animation
  - Likely using CSS animation or JavaScript

**Marquee Implementation:**
```css
/* CSS Marquee Animation */
@keyframes marquee {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}

.marquee {
  display: flex;
  animation: marquee 20s linear infinite;
  white-space: nowrap;
}
```

**Styling:**
- Dark background (black or dark purple)
- White/gray text
- Links: White with hover effects
- Icons: White, medium size
- Copyright: Small text, gray

### Design Patterns Summary

#### Color Usage
- **Hero/Intro**: Dark purple/black gradient background
- **Logo Section**: White or light background
- **Value Cards**: Soft, semi-transparent backgrounds
- **Awards**: Light or dark (theme-dependent)
- **Team Cards**: Pastel gradients (blue, pink, yellow, purple)
- **Footer**: Dark background

#### Typography Hierarchy
1. **Section Headings (H2)**: 48px-64px, bold, white
2. **Card Titles (H3)**: 24px-32px, bold, black/white
3. **Body Text**: 16px-18px, regular, white/gray
4. **Small Text**: 14px, regular, gray
5. **Names**: 18px-24px, bold, black
6. **Titles/Roles**: 14px-16px, regular, gray

#### Spacing System
- **Section spacing**: 80px-120px between major sections
- **Card spacing**: 24px-32px between cards
- **Card padding**: 24px-32px internal padding
- **Vertical rhythm**: Consistent spacing multiples (8px base)

#### Animation Patterns
1. **Scroll Animations**: Fade in, slide up as sections enter viewport
2. **Stagger Effects**: Cards animate in sequence (50ms-100ms delay)
3. **Hover Effects**: Scale transforms, shadow increases, color transitions
4. **Marquee**: Continuous horizontal scrolling animation
5. **Smooth Transitions**: 200ms-300ms for all interactive elements

### Implementation Recommendations for TradeSignal

#### About Page Structure
```
<AboutPage>
  <GlassmorphicNav />
  <AboutHeroSection />
  <CompanyValuesSection /> (3 value cards)
  <AchievementsSection /> (Awards/Recognition)
  <TeamSection /> (Optional - if TradeSignal has team)
  <CTASection />
  <LandingFooter />
</AboutPage>
```

#### Component Adaptations

**Value Cards Component:**
- Reuse FeatureCard component with numbered labels
- Adapt content to TradeSignal values:
  - Real-time data accuracy
  - AI-powered insights
  - User-focused design

**Team Cards Component:**
- Create TeamMemberCard component
- Use pastel gradient backgrounds
- Include profile images, names, roles
- Add social media links if applicable

**Awards Section:**
- Create AchievementCard component
- Display TradeSignal achievements, milestones, or certifications
- Use icon + text + date format

**Marquee Component:**
- Create reusable Marquee component
- Use for announcements, availability, or key messages
- Implement smooth CSS animation

### Technical Implementation Notes

#### Team Cards CSS
```css
.team-card {
  background: linear-gradient(135deg, var(--card-gradient-1));
  border-radius: 24px;
  padding: 32px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.team-card:hover {
  transform: scale(1.02);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.team-card-gradient-1 {
  background: linear-gradient(135deg, #E0F2FE 0%, #DBEAFE 100%);
}

.team-card-gradient-2 {
  background: linear-gradient(135deg, #FCE7F3 0%, #F3E8FF 100%);
}

.team-card-gradient-3 {
  background: linear-gradient(135deg, #FEF3C7 0%, #FED7AA 100%);
}

.team-card-gradient-4 {
  background: linear-gradient(135deg, #E0E7FF 0%, #DDD6FE 100%);
}
```

#### Marquee Animation
```tsx
// React Component
const Marquee = ({ text, speed = 20 }) => {
  return (
    <div className="overflow-hidden whitespace-nowrap">
      <div 
        className="inline-flex animate-marquee"
        style={{ animationDuration: `${speed}s` }}
      >
        {[...Array(10)].map((_, i) => (
          <span key={i} className="mx-8">{text}</span>
        ))}
      </div>
    </div>
  );
};
```

### Key Takeaways for TradeSignal

1. **Section Variety**: Use different background treatments for visual interest
2. **Card Design**: Pastel gradients work well for team/value cards
3. **Numbering System**: Numbered labels (01, 02, 03) add structure
4. **Animation**: Staggered scroll animations create engaging experience
5. **Marquee**: Animated text can highlight key messages
6. **Responsive**: All sections adapt well to mobile/tablet
7. **Typography**: Clear hierarchy with size, weight, and color
8. **Spacing**: Generous spacing creates breathing room

## Detailed Analysis: Layzo Privacy Policy & Terms & Conditions Pages

This section provides comprehensive analysis of the Layzo Privacy Policy (https://layzo.webflow.io/privacy-policy) and Terms & Conditions (https://layzo.webflow.io/terms-condition) pages to understand the design patterns, layout structure, and content organization that can be adapted for TradeSignal's legal pages.

### Privacy Policy Page Analysis

#### Page Structure Overview

The Privacy Policy page follows a clean, content-focused design with the following structure:
1. **Header/Navigation** - Standard glassmorphism navigation bar
2. **Hero Section** - Large heading "Privacy Policy" with introductory statement
3. **Content Sections** - Multiple well-organized sections with clear headings
4. **CTA Section** - "Buy Template" button (template-specific, not needed for TradeSignal)
5. **Footer** - Standard footer with navigation links

#### Visual Design Elements

**Hero Section:**
- Large "Privacy Policy" heading (H1, white text on dark background)
- Introductory paragraph: "At Layzo, your privacy matters. This policy outlines how we collect, use, and protect your information when you use our services."
- Clean, centered or left-aligned layout
- Dark background consistent with site theme

**Content Layout:**
- White or light background for main content area
- Dark text for readability
- Generous spacing between sections
- Clear typography hierarchy

**Typography:**
- Main heading: Large (48px-64px), bold, dark/white
- Section headings (H2): Medium-large (32px-40px), bold
- Body text: Regular (16px-18px), readable line-height (1.6-1.8)
- Bullet points: Well-spaced, easy to scan

#### Content Structure

**Section 1: Information We Collect**
- Heading: "Information We Collect"
- Bullet list format with categories:
  - Personal Information
  - Usage Data
  - Device & Technical Data
  - Communications
- Each bullet has a brief description

**Section 2: How We Use Your Information**
- Heading: "How We Use Your Information"
- Bullet list format:
  - Provide, operate, and improve services
  - Process transactions
  - Respond to inquiries
  - Send updates and communications
  - Ensure security and compliance

**Section 3: Sharing of Information**
- Heading: "Sharing of Information"
- Opening statement: "We do not sell your personal information."
- Sub-sections for sharing scenarios:
  - Service Providers
  - Legal Authorities
  - Business Transfers

**Section 4: Cookies & Tracking Technologies**
- Heading: "Cookies & Tracking Technologies"
- Brief explanation of cookie usage
- Note about browser controls

**Section 5: Data Security**
- Heading: "Data Security"
- Statement about security measures
- Disclaimer about no 100% guarantee

**Section 6: Third-Party Links**
- Heading: "Third-Party Links"
- Disclaimer about external sites

**Section 7: Changes to This Policy**
- Heading: "Changes to This Policy"
- Statement about policy updates
- Note about "Last Updated" date

**Section 8: Contact Us**
- Heading: "Contact Us"
- Contact email: support@layzo@gmail.com
- Invitation for questions/concerns

#### Design Patterns

**Layout:**
- Max-width container (1280px) for readability
- Centered or left-aligned content
- Consistent padding (24px-48px)
- Section spacing: 48px-64px between major sections

**Content Formatting:**
- Clear section headings
- Bullet lists for easy scanning
- Short paragraphs (2-4 sentences)
- Bold text for emphasis on key points
- Contact information prominently displayed

**Styling:**
- Clean, professional appearance
- High contrast for readability
- No distracting elements
- Focus on content clarity

### Terms & Conditions Page Analysis

#### Page Structure Overview

The Terms & Conditions page follows a similar structure to the Privacy Policy:
1. **Header/Navigation** - Standard glassmorphism navigation bar
2. **Hero Section** - Large heading "Terms & Conditions" with introductory statement
3. **Content Sections** - Multiple well-organized sections
4. **CTA Section** - "Buy Template" button (template-specific)
5. **Footer** - Standard footer

#### Visual Design Elements

**Hero Section:**
- Large "Terms & Conditions" heading (H1)
- Introductory paragraph: "Welcome to Layzo. By accessing or using our website, products, or services, you agree to these Terms & Conditions. Please read them carefully."
- Same design treatment as Privacy Policy

**Content Layout:**
- Consistent with Privacy Policy design
- White/light background
- Dark text
- Clear section separation

#### Content Structure

**Section 1: Acceptance of Terms**
- Heading: "Acceptance of Terms"
- Age requirement statement
- Agreement confirmation
- Option to not use services if disagree

**Section 2: Use of Services**
- Heading: "Use of Services"
- Bullet list format:
  - Lawful purposes only
  - No hacking/disruption
  - Right to suspend/terminate

**Section 3: Accounts & Registration**
- Heading: "Accounts & Registration"
- Bullet list:
  - Account creation requirements
  - Security responsibilities
  - Accurate information requirement

**Section 4: Purchases & Payments**
- Heading: "Purchases & Payments"
- Bullet list:
  - Payment methods
  - Price change policy
  - Refund policy reference

**Section 5: Intellectual Property**
- Heading: "Intellectual Property"
- Ownership statement
- Usage restrictions

**Section 6: Third-Party Links**
- Heading: "Third-Party Links"
- Disclaimer about external content

**Section 7: Limitation of Liability**
- Heading: "Limitation of Liability"
- "As is" and "As available" statements
- Damage disclaimer
- Liability limitation statement

**Section 8: Termination**
- Heading: "Termination"
- Right to suspend/terminate
- Violation consequences

**Section 9: Changes to Terms**
- Heading: "Changes to Terms"
- Update policy
- "Last Updated" date mention
- Continued use acceptance

**Section 10: Contact Us**
- Heading: "Contact Us"
- Contact email: support@layzo@gmail.com

#### Design Patterns

**Layout:**
- Same as Privacy Policy
- Max-width container
- Consistent spacing
- Clear hierarchy

**Content Formatting:**
- Section headings with clear hierarchy
- Bullet lists for key points
- Short, scannable paragraphs
- Bold emphasis on important statements
- Contact information at end

### Implementation Recommendations for TradeSignal

#### Privacy Policy Page Structure

```tsx
<PrivacyPolicyPage>
  <GlassmorphicNav />
  <LegalHeroSection 
    title="Privacy Policy"
    intro="At TradeSignal, your privacy matters. This policy outlines how we collect, use, and protect your information when you use our services."
  />
  <LegalContentSection>
    <Section title="Information We Collect">
      {/* Bullet list of data types */}
    </Section>
    <Section title="How We Use Your Information">
      {/* Bullet list of usage purposes */}
    </Section>
    <Section title="Sharing of Information">
      {/* Sharing scenarios */}
    </Section>
    <Section title="Cookies & Tracking Technologies">
      {/* Cookie policy */}
    </Section>
    <Section title="Data Security">
      {/* Security measures */}
    </Section>
    <Section title="Third-Party Links">
      {/* Disclaimer */}
    </Section>
    <Section title="Changes to This Policy">
      {/* Update policy */}
    </Section>
    <Section title="Contact Us">
      {/* Contact information */}
    </Section>
  </LegalContentSection>
  <LandingFooter />
</PrivacyPolicyPage>
```

#### Terms & Conditions Page Structure

```tsx
<TermsOfServicePage>
  <GlassmorphicNav />
  <LegalHeroSection 
    title="Terms & Conditions"
    intro="Welcome to TradeSignal. By accessing or using our website, products, or services, you agree to these Terms & Conditions. Please read them carefully."
  />
  <LegalContentSection>
    <Section title="Acceptance of Terms">
      {/* Age and agreement requirements */}
    </Section>
    <Section title="Use of Services">
      {/* Usage rules */}
    </Section>
    <Section title="Accounts & Registration">
      {/* Account requirements */}
    </Section>
    <Section title="Purchases & Payments">
      {/* Payment terms */}
    </Section>
    <Section title="Intellectual Property">
      {/* IP rights */}
    </Section>
    <Section title="Third-Party Links">
      {/* Disclaimer */}
    </Section>
    <Section title="Limitation of Liability">
      {/* Liability disclaimers */}
    </Section>
    <Section title="Termination">
      {/* Termination policy */}
    </Section>
    <Section title="Changes to Terms">
      {/* Update policy */}
    </Section>
    <Section title="Contact Us">
      {/* Contact information */}
    </Section>
  </LegalContentSection>
  <LandingFooter />
</TermsOfServicePage>
```

#### Reusable Components

**LegalHeroSection Component:**
```tsx
interface LegalHeroSectionProps {
  title: string;
  intro: string;
}

const LegalHeroSection = ({ title, intro }: LegalHeroSectionProps) => {
  return (
    <div className="bg-gradient-to-br from-purple-900 via-purple-800 to-purple-900 py-20 px-4">
      <div className="max-w-4xl mx-auto text-center">
        <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
          {title}
        </h1>
        <p className="text-xl text-purple-100 max-w-3xl mx-auto">
          {intro}
        </p>
      </div>
    </div>
  );
};
```

**LegalContentSection Component:**
```tsx
const LegalContentSection = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="bg-white py-16 px-4">
      <div className="max-w-4xl mx-auto prose prose-lg">
        {children}
      </div>
    </div>
  );
};
```

**Section Component:**
```tsx
interface SectionProps {
  title: string;
  children: React.ReactNode;
}

const Section = ({ title, children }: SectionProps) => {
  return (
    <section className="mb-12">
      <h2 className="text-3xl font-bold text-gray-900 mb-6">
        {title}
      </h2>
      <div className="text-gray-700 leading-relaxed">
        {children}
      </div>
    </section>
  );
};
```

#### Content Formatting Guidelines

**Bullet Lists:**
- Use consistent bullet style (• or -)
- Spacing: 16px-24px between items
- Nested lists: 8px-12px indentation
- Bold category names, regular descriptions

**Paragraphs:**
- Max 4-5 sentences per paragraph
- Line height: 1.6-1.8 for readability
- Spacing: 16px-24px between paragraphs

**Headings:**
- H1: 48px-64px (hero section only)
- H2: 32px-40px (section headings)
- H3: 24px-28px (sub-sections if needed)
- Font weight: 700 for headings

**Contact Information:**
- Prominently displayed at end
- Email: support@tradesignal.com (or your actual email)
- Styled as link with hover effect
- Clear call-to-action: "If you have questions..."

#### Styling Specifications

**Hero Section:**
```css
.legal-hero {
  background: linear-gradient(135deg, #1E1B4B 0%, #312E81 50%, #4C1D95 100%);
  padding: 80px 24px;
  text-align: center;
}

.legal-hero h1 {
  color: #FFFFFF;
  font-size: 48px-64px;
  font-weight: 700;
  margin-bottom: 24px;
}

.legal-hero p {
  color: #C4B5FD;
  font-size: 20px-24px;
  max-width: 768px;
  margin: 0 auto;
}
```

**Content Section:**
```css
.legal-content {
  background: #FFFFFF;
  padding: 64px 24px;
  max-width: 1024px;
  margin: 0 auto;
}

.legal-content section {
  margin-bottom: 48px;
}

.legal-content h2 {
  color: #1F2937;
  font-size: 32px-40px;
  font-weight: 700;
  margin-bottom: 24px;
}

.legal-content p {
  color: #4B5563;
  font-size: 16px-18px;
  line-height: 1.7;
  margin-bottom: 16px;
}

.legal-content ul {
  list-style: disc;
  margin-left: 24px;
  margin-bottom: 16px;
}

.legal-content li {
  color: #4B5563;
  font-size: 16px-18px;
  line-height: 1.7;
  margin-bottom: 12px;
}
```

#### TradeSignal-Specific Content Adaptations

**Privacy Policy Sections:**
1. **Information We Collect:**
   - Personal Information: Email, username, payment details
   - Trading Data: Watchlists, alerts, preferences
   - Usage Data: Pages visited, features used, time spent
   - Device Data: IP address, browser, device information
   - Communication Data: Support tickets, feedback

2. **How We Use Your Information:**
   - Provide insider trading data and analytics
   - Process subscription payments
   - Send trade alerts and notifications
   - Improve AI-powered insights
   - Customer support and communication
   - Security and fraud prevention

3. **Sharing of Information:**
   - SEC data providers (public data)
   - Payment processors (Stripe)
   - Analytics services (anonymized)
   - Legal compliance when required

**Terms & Conditions Sections:**
1. **Use of Services:**
   - Financial data is for informational purposes only
   - Not providing investment advice
   - Users responsible for their trading decisions
   - Prohibited: Automated scraping, data resale

2. **Accounts & Registration:**
   - One account per user
   - Accurate information required
   - Account security responsibility
   - Age requirement: 18+ (or with guardian consent)

3. **Purchases & Payments:**
   - Subscription-based service
   - Auto-renewal terms
   - Cancellation policy
   - Refund policy (if applicable)

4. **Intellectual Property:**
   - TradeSignal platform and data ownership
   - User-generated content rights
   - SEC data: Public domain, but presentation is proprietary

5. **Limitation of Liability:**
   - Financial disclaimer
   - Data accuracy disclaimer
   - Service availability disclaimer
   - No investment advice disclaimer

#### Responsive Design

**Mobile (< 640px):**
- Hero heading: 36px-40px
- Section headings: 24px-28px
- Padding: 16px-24px
- Font size: 14px-16px

**Tablet (640px - 1024px):**
- Hero heading: 48px-56px
- Section headings: 28px-32px
- Padding: 24px-32px
- Font size: 16px-18px

**Desktop (> 1024px):**
- Hero heading: 56px-64px
- Section headings: 32px-40px
- Padding: 32px-48px
- Font size: 16px-18px

#### Key Takeaways

1. **Content-First Design**: Legal pages prioritize readability over visual flair
2. **Clear Hierarchy**: Use consistent heading sizes and spacing
3. **Scannable Format**: Bullet lists and short paragraphs improve readability
4. **Professional Appearance**: Clean, minimal design builds trust
5. **Consistent Styling**: Match hero section with site theme
6. **Contact Prominence**: Make contact information easy to find
7. **Regular Updates**: Include "Last Updated" date mechanism
8. **Mobile-Friendly**: Ensure readability on all devices

## Detailed Analysis: Layzo Style Guide Page

This section provides a comprehensive analysis of the Layzo Style Guide page (https://layzo.webflow.io/style-guide) with exact specifications for colors, typography, buttons, and design tokens that Gemini must implement precisely for TradeSignal.

### Page Structure Overview

The Style Guide page is organized into clear sections:
1. **Header/Navigation** - Standard glassmorphism navigation bar
2. **Hero Section** - "Style Guide" heading with introductory text
3. **Colors Style Section** - Organized color palette with categories
4. **Typography Styles Section** - Complete typography system
5. **Buttons Style Section** - Button variants and sizes
6. **Footer** - Standard footer

### Colors Style - Exact Specifications

#### Brand Colors

**Primary Color:**
- Hex: `#6766FF`
- Usage: Primary buttons, links, accents, brand elements
- RGB: `rgb(103, 102, 255)`
- This is the main brand purple color used throughout the site

#### Text Colors

**Title White:**
- Hex: `#FFFFFF`
- Usage: White text on dark backgrounds
- RGB: `rgb(255, 255, 255)`

**Paragraph Grey:**
- Hex: `#E1E2E5`
- Usage: Secondary text, descriptions on dark backgrounds
- RGB: `rgb(225, 226, 229)`

**Paragraph Dark:**
- Hex: `#767676`
- Usage: Secondary text on light backgrounds
- RGB: `rgb(118, 118, 118)`

**Title Black:**
- Hex: `#03020B`
- Usage: Primary headings on light backgrounds
- RGB: `rgb(3, 2, 11)`

#### Background Colors

**Blue Gradient:**
- Start: `#F6F9FF`
- End: `#FFFFFF`
- Usage: Light blue gradient backgrounds
- Direction: Top to bottom (or as specified)

**Pink Gradient:**
- Start: `#FFFFFF`
- End: `#FFEFFA`
- Usage: Light pink gradient backgrounds
- Direction: Top to bottom (or as specified)

**Blue Gradient 2:**
- Start: `#E9EFFF`
- End: `#FFFFFF`
- Usage: Alternative blue gradient backgrounds
- Direction: Top to bottom (or as specified)

**White:**
- Hex: `#FFFFFF`
- Usage: Primary light background
- RGB: `rgb(255, 255, 255)`

**Grey:**
- Hex: `#F6F6F6`
- Usage: Light grey backgrounds, subtle sections
- RGB: `rgb(246, 246, 246)`

**Dark:**
- Hex: `#03020B`
- Usage: Dark backgrounds, hero sections
- RGB: `rgb(3, 2, 11)`

#### Border Colors

**Stroke Light:**
- Hex: `#E1E2E5`
- Usage: Light borders, dividers
- RGB: `rgb(225, 226, 229)`

**Stroke Dark:**
- Hex: `#595959`
- Usage: Dark borders, emphasis
- RGB: `rgb(89, 89, 89)`

### Typography Styles - Exact Specifications

#### Font Family

**Primary Font: TASA Orbiter Display**
- Available weights: Regular, Medium, SemiBold, Bold
- Usage: All headings and body text
- Fallback: Modern sans-serif (Inter, Poppins, or system fonts if TASA Orbiter not available)

**Note:** If TASA Orbiter Display is not available, use a similar modern display font or fallback to Inter/Poppins with similar characteristics.

#### Heading Styles

**H1 Text:**
- Font: TASA Orbiter Display
- Weight: Medium
- Size: `96px`
- Line Height: `100%` (96px)
- Usage: Main page headings, hero sections

**H2 Text:**
- Font: TASA Orbiter Display
- Weight: Medium
- Size: `80px`
- Line Height: `100%` (80px)
- Usage: Section headings

**H3 Text:**
- Font: TASA Orbiter Display
- Weight: Medium
- Size: `60px`
- Line Height: `110%` (66px)
- Usage: Subsection headings

**H4 Text:**
- Font: TASA Orbiter Display
- Weight: Medium
- Size: `48px`
- Line Height: `120%` (57.6px)
- Usage: Card titles, feature headings

**H5 Text:**
- Font: TASA Orbiter Display
- Weight: Medium
- Size: `40px`
- Line Height: `120%` (48px)
- Usage: Smaller section headings

**H6 Text:**
- Font: TASA Orbiter Display
- Weight: Medium
- Size: `28px`
- Line Height: `130%` (36.4px)
- Usage: Small headings, labels

#### Paragraph Text Styles

**Para Text Extra Large:**
- Font: TASA Orbiter Display
- Weight: Medium
- Size: `24px`
- Line Height: `160%` (38.4px)
- Usage: Large body text, introductions

**Para Text Large:**
- Font: TASA Orbiter Display
- Weight: Medium
- Size: `20px`
- Line Height: `160%` (32px)
- Usage: Important body text

**Para Text Medium:**
- Font: TASA Orbiter Display
- Weight: Medium
- Size: `18px`
- Line Height: `150%` (27px)
- Usage: Standard body text

**Para Text Small:**
- Font: TASA Orbiter Display
- Weight: Medium
- Size: `16px`
- Line Height: `150%` (24px)
- Usage: Secondary text, descriptions

**Para Text Extra Small:**
- Font: TASA Orbiter Display
- Weight: Medium
- Size: `14px`
- Line Height: `150%` (21px)
- Usage: Captions, fine print

#### Button Text Styles

**Button Text:**
- Font: TASA Orbiter Display
- Weight: Medium
- Size: `18px`
- Line Height: `100%` (18px)
- Usage: Large buttons

**Button Text Medium:**
- Font: TASA Orbiter Display
- Weight: Medium
- Size: `16px`
- Line Height: `100%` (16px)
- Usage: Medium/small buttons

### Buttons Style - Exact Specifications

#### Button Large

**Primary Button (Large):**
- Background: Primary Color (`#6766FF`)
- Text: White (`#FFFFFF`)
- Text Size: `18px` (Button Text)
- Padding: (Estimate: 16px-24px vertical, 32px-48px horizontal)
- Border Radius: (Estimate: 8px-12px)
- Hover: Slightly darker shade or brightness adjustment

**Secondary Button (Large):**
- Background: Transparent or light
- Text: Primary Color (`#6766FF`) or dark
- Border: Primary Color (`#6766FF`) or Stroke Dark
- Text Size: `18px` (Button Text)
- Padding: Same as Primary
- Border Radius: Same as Primary

**Ghost Button (Large):**
- Background: Transparent
- Text: Primary Color (`#6766FF`) or dark
- Border: None or subtle
- Text Size: `18px` (Button Text)
- Padding: Same as Primary
- Border Radius: Same as Primary

#### Button Small

**Primary Button (Small):**
- Background: Primary Color (`#6766FF`)
- Text: White (`#FFFFFF`)
- Text Size: `16px` (Button Text Medium)
- Padding: (Estimate: 12px-16px vertical, 24px-32px horizontal)
- Border Radius: (Estimate: 6px-10px)

**Secondary Button (Small):**
- Background: Transparent or light
- Text: Primary Color (`#6766FF`) or dark
- Border: Primary Color (`#6766FF`) or Stroke Dark
- Text Size: `16px` (Button Text Medium)
- Padding: Same as Primary Small
- Border Radius: Same as Primary Small

**Ghost Button (Small):**
- Background: Transparent
- Text: Primary Color (`#6766FF`) or dark
- Border: None or subtle
- Text Size: `16px` (Button Text Medium)
- Padding: Same as Primary Small
- Border Radius: Same as Primary Small

### Implementation Specifications

#### CSS Variables/Tokens

```css
:root {
  /* Brand Colors */
  --color-primary: #6766FF;
  
  /* Text Colors */
  --color-text-title-white: #FFFFFF;
  --color-text-paragraph-grey: #E1E2E5;
  --color-text-paragraph-dark: #767676;
  --color-text-title-black: #03020B;
  
  /* Background Colors */
  --color-bg-blue-gradient-start: #F6F9FF;
  --color-bg-blue-gradient-end: #FFFFFF;
  --color-bg-pink-gradient-start: #FFFFFF;
  --color-bg-pink-gradient-end: #FFEFFA;
  --color-bg-blue-gradient-2-start: #E9EFFF;
  --color-bg-blue-gradient-2-end: #FFFFFF;
  --color-bg-white: #FFFFFF;
  --color-bg-grey: #F6F6F6;
  --color-bg-dark: #03020B;
  
  /* Border Colors */
  --color-border-stroke-light: #E1E2E5;
  --color-border-stroke-dark: #595959;
  
  /* Typography - Headings */
  --font-heading-h1-size: 96px;
  --font-heading-h1-line-height: 100%;
  --font-heading-h2-size: 80px;
  --font-heading-h2-line-height: 100%;
  --font-heading-h3-size: 60px;
  --font-heading-h3-line-height: 110%;
  --font-heading-h4-size: 48px;
  --font-heading-h4-line-height: 120%;
  --font-heading-h5-size: 40px;
  --font-heading-h5-line-height: 120%;
  --font-heading-h6-size: 28px;
  --font-heading-h6-line-height: 130%;
  
  /* Typography - Paragraphs */
  --font-para-extra-large-size: 24px;
  --font-para-extra-large-line-height: 160%;
  --font-para-large-size: 20px;
  --font-para-large-line-height: 160%;
  --font-para-medium-size: 18px;
  --font-para-medium-line-height: 150%;
  --font-para-small-size: 16px;
  --font-para-small-line-height: 150%;
  --font-para-extra-small-size: 14px;
  --font-para-extra-small-line-height: 150%;
  
  /* Typography - Buttons */
  --font-button-large-size: 18px;
  --font-button-large-line-height: 100%;
  --font-button-medium-size: 16px;
  --font-button-medium-line-height: 100%;
  
  /* Font Family */
  --font-family-primary: 'TASA Orbiter Display', 'Inter', 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-weight-regular: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
}
```

#### Tailwind Configuration

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      fontFamily: {
        'display': ['TASA Orbiter Display', 'Inter', 'Poppins', 'sans-serif'],
      },
      colors: {
        primary: {
          DEFAULT: '#6766FF',
        },
        text: {
          'title-white': '#FFFFFF',
          'paragraph-grey': '#E1E2E5',
          'paragraph-dark': '#767676',
          'title-black': '#03020B',
        },
        bg: {
          'blue-gradient-start': '#F6F9FF',
          'blue-gradient-end': '#FFFFFF',
          'pink-gradient-start': '#FFFFFF',
          'pink-gradient-end': '#FFEFFA',
          'blue-gradient-2-start': '#E9EFFF',
          'blue-gradient-2-end': '#FFFFFF',
          'grey': '#F6F6F6',
          'dark': '#03020B',
        },
        border: {
          'stroke-light': '#E1E2E5',
          'stroke-dark': '#595959',
        },
      },
      fontSize: {
        'h1': ['96px', { lineHeight: '100%', fontWeight: '500' }],
        'h2': ['80px', { lineHeight: '100%', fontWeight: '500' }],
        'h3': ['60px', { lineHeight: '110%', fontWeight: '500' }],
        'h4': ['48px', { lineHeight: '120%', fontWeight: '500' }],
        'h5': ['40px', { lineHeight: '120%', fontWeight: '500' }],
        'h6': ['28px', { lineHeight: '130%', fontWeight: '500' }],
        'para-xl': ['24px', { lineHeight: '160%', fontWeight: '500' }],
        'para-lg': ['20px', { lineHeight: '160%', fontWeight: '500' }],
        'para-md': ['18px', { lineHeight: '150%', fontWeight: '500' }],
        'para-sm': ['16px', { lineHeight: '150%', fontWeight: '500' }],
        'para-xs': ['14px', { lineHeight: '150%', fontWeight: '500' }],
        'btn-lg': ['18px', { lineHeight: '100%', fontWeight: '500' }],
        'btn-md': ['16px', { lineHeight: '100%', fontWeight: '500' }],
      },
    },
  },
}
```

#### Typography Classes

```css
/* Headings */
.h1-text {
  font-family: var(--font-family-primary);
  font-size: 96px;
  font-weight: 500;
  line-height: 100%;
}

.h2-text {
  font-family: var(--font-family-primary);
  font-size: 80px;
  font-weight: 500;
  line-height: 100%;
}

.h3-text {
  font-family: var(--font-family-primary);
  font-size: 60px;
  font-weight: 500;
  line-height: 110%;
}

.h4-text {
  font-family: var(--font-family-primary);
  font-size: 48px;
  font-weight: 500;
  line-height: 120%;
}

.h5-text {
  font-family: var(--font-family-primary);
  font-size: 40px;
  font-weight: 500;
  line-height: 120%;
}

.h6-text {
  font-family: var(--font-family-primary);
  font-size: 28px;
  font-weight: 500;
  line-height: 130%;
}

/* Paragraphs */
.para-text-xl {
  font-family: var(--font-family-primary);
  font-size: 24px;
  font-weight: 500;
  line-height: 160%;
}

.para-text-lg {
  font-family: var(--font-family-primary);
  font-size: 20px;
  font-weight: 500;
  line-height: 160%;
}

.para-text-md {
  font-family: var(--font-family-primary);
  font-size: 18px;
  font-weight: 500;
  line-height: 150%;
}

.para-text-sm {
  font-family: var(--font-family-primary);
  font-size: 16px;
  font-weight: 500;
  line-height: 150%;
}

.para-text-xs {
  font-family: var(--font-family-primary);
  font-size: 14px;
  font-weight: 500;
  line-height: 150%;
}

/* Buttons */
.btn-text-lg {
  font-family: var(--font-family-primary);
  font-size: 18px;
  font-weight: 500;
  line-height: 100%;
}

.btn-text-md {
  font-family: var(--font-family-primary);
  font-size: 16px;
  font-weight: 500;
  line-height: 100%;
}
```

#### Button Component Styles

```css
/* Button Large - Primary */
.btn-large-primary {
  background-color: var(--color-primary);
  color: var(--color-text-title-white);
  font-size: 18px;
  font-weight: 500;
  line-height: 100%;
  padding: 16px 32px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-large-primary:hover {
  background-color: #5A59E6; /* Slightly darker */
  transform: translateY(-1px);
}

/* Button Large - Secondary */
.btn-large-secondary {
  background-color: transparent;
  color: var(--color-primary);
  border: 2px solid var(--color-primary);
  font-size: 18px;
  font-weight: 500;
  line-height: 100%;
  padding: 16px 32px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-large-secondary:hover {
  background-color: var(--color-primary);
  color: var(--color-text-title-white);
}

/* Button Large - Ghost */
.btn-large-ghost {
  background-color: transparent;
  color: var(--color-primary);
  border: none;
  font-size: 18px;
  font-weight: 500;
  line-height: 100%;
  padding: 16px 32px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-large-ghost:hover {
  background-color: rgba(103, 102, 255, 0.1);
}

/* Button Small - Primary */
.btn-small-primary {
  background-color: var(--color-primary);
  color: var(--color-text-title-white);
  font-size: 16px;
  font-weight: 500;
  line-height: 100%;
  padding: 12px 24px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-small-primary:hover {
  background-color: #5A59E6;
  transform: translateY(-1px);
}

/* Button Small - Secondary */
.btn-small-secondary {
  background-color: transparent;
  color: var(--color-primary);
  border: 2px solid var(--color-primary);
  font-size: 16px;
  font-weight: 500;
  line-height: 100%;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-small-secondary:hover {
  background-color: var(--color-primary);
  color: var(--color-text-title-white);
}

/* Button Small - Ghost */
.btn-small-ghost {
  background-color: transparent;
  color: var(--color-primary);
  border: none;
  font-size: 16px;
  font-weight: 500;
  line-height: 100%;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-small-ghost:hover {
  background-color: rgba(103, 102, 255, 0.1);
}
```

#### React Button Component Example

```tsx
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'large' | 'small';
  children: React.ReactNode;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  disabled?: boolean;
}

const Button = ({ 
  variant = 'primary', 
  size = 'large', 
  children, 
  onClick,
  type = 'button',
  disabled = false
}: ButtonProps) => {
  const baseClasses = 'font-display font-medium transition-all duration-300 cursor-pointer';
  const variantClasses = {
    primary: 'bg-primary text-text-title-white hover:bg-[#5A59E6]',
    secondary: 'bg-transparent text-primary border-2 border-primary hover:bg-primary hover:text-text-title-white',
    ghost: 'bg-transparent text-primary hover:bg-primary/10',
  };
  const sizeClasses = {
    large: 'text-btn-lg px-8 py-4 rounded-lg',
    small: 'text-btn-md px-6 py-3 rounded-md',
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${
        disabled ? 'opacity-50 cursor-not-allowed' : ''
      }`}
    >
      {children}
    </button>
  );
};
```

### Responsive Typography Scaling

For mobile devices, scale down the typography while maintaining proportions:

**Mobile (< 640px):**
- H1: 48px (50% of desktop)
- H2: 40px (50% of desktop)
- H3: 30px (50% of desktop)
- H4: 24px (50% of desktop)
- H5: 20px (50% of desktop)
- H6: 18px (64% of desktop)
- Para XL: 18px (75% of desktop)
- Para LG: 16px (80% of desktop)
- Para MD: 16px (89% of desktop)
- Para SM: 14px (87.5% of desktop)
- Para XS: 12px (86% of desktop)

**Tablet (640px - 1024px):**
- H1: 64px (67% of desktop)
- H2: 56px (70% of desktop)
- H3: 42px (70% of desktop)
- H4: 36px (75% of desktop)
- H5: 32px (80% of desktop)
- H6: 24px (86% of desktop)
- Other sizes: 85-90% of desktop

### Key Implementation Notes

1. **Font Loading**: If using TASA Orbiter Display, ensure proper font loading with fallbacks
2. **Exact Sizes**: Use the exact pixel sizes specified - do not round or approximate
3. **Line Heights**: Use percentages as specified (100%, 110%, 120%, 130%, 150%, 160%)
4. **Font Weight**: All text uses Medium (500) weight unless specified otherwise
5. **Color Accuracy**: Use exact hex codes provided - no variations
6. **Consistency**: Apply these styles consistently across all TradeSignal pages
7. **Responsive**: Scale appropriately for mobile while maintaining design integrity

### TradeSignal Color Adaptation

While implementing the exact Layzo style guide, TradeSignal can adapt:
- **Primary Color**: Keep `#6766FF` or adjust to TradeSignal brand purple
- **Gradients**: Use the gradient specifications for hero sections and backgrounds
- **Text Colors**: Maintain the text color hierarchy for readability
- **Backgrounds**: Use appropriate backgrounds (dark for hero, light for content)

---

**End of Implementation Guide**

This document provides all necessary information for implementing the TradeSignal landing page. Follow the structure, use the provided code examples, and adapt the content to showcase TradeSignal's specific features and value propositions.
