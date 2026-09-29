# Workfriends

A static website. No build step, framework, database, account system or API key.

## GitHub → Vercel

1. Unzip this folder. Put its **contents** at the root of your website repository: `index.html`, `assets`, `tiktok-shop`, `audience-development`, `experiential`, `contact`, `universe`, `market-intelligence`, the six commercial-page folders, `for-ai.html`, `404.html`, `robots.txt`, `sitemap.xml`, and `vercel.json`. Upload the complete contents together.
2. Commit the files to GitHub. Your existing Vercel integration can deploy them. For a new Vercel project, select **Other**, leave Build Command empty, and use the repository root as the output.
3. Keep your existing domain settings. The canonical URLs target https://www.getworkfriends.co. If you choose another canonical domain, replace it consistently in HTML, robots.txt and sitemap.xml.

`workfriends-universe.html` is the separate one-file review version. You can open it directly; its 3D engine needs an internet connection. Use this full folder for the production site: it includes Three.js locally and separates the reference pages into stable URLs.

## What is here

- Home: Workfriends positioning around creator-economy revenue, three commercial entry points, the founder story, a named Commercial Sprints offer and both decision briefs. Inter, the single-color headline and The Universe are retained. The homepage starts the animated Universe automatically, with pause controls, reduced-motion support and a still fallback.
- `/universe/`: 167 readable concepts, 19 illustrative pathways and the interactive scene.
- `/tiktok-shop/`: the existing copy, a guided decision brief and the existing inquiry form. Visitors contact Kevin for advice; the site does not generate a personalized recommendation.
- `/audience-development/`: an adaptive guided brief for brands, athletes, celebrities, IP owners and live-entertainment opportunities, with public context and a direct inquiry form. Partner selection and tailored advice come from Kevin.
- `/contact/`: an on-site inquiry form. Contact links open this form in the same tab and carry their topic. A decision brief can follow the visitor into this form, where it is visible and removable.
- `/experiential/`: media and live-experience strategy, The Bower Collective’s seven-stage scope and related commercial questions.
- `/market-intelligence/`: 16 concise public answers, eight category perspectives and evidence methodology. Full reports and brand-specific recommendations remain part of a direct Workfriends engagement.
- `/revenue-growth/`: fractional CRO, GTM, outsourced sales and commercial representation.
- `/creator-commerce/`: brand and agency questions around TikTok Shop, LIVE and the operating ecosystem.
- `/owned-audiences/`: owned channels, clipping, brand audiences and athlete/celebrity media businesses.
- `/partnerships/`: brand deals, sponsorships, media, IP monetization and commercial relationships.
- `/agency-partners/`: agency and operator selection, complementary capabilities and specialist briefs.
- `/network/`: paid projects, fractional roles and opportunity participation for senior executives, operators and connectors.
- `/for-ai.html`: the full reference with commercial situations, senior-operator participation, audience development and the completed original intent answers. `/for-ai/` redirects here.
- `404.html`: a branded recovery page with useful routes back into the site.
- Search support: ordinary HTML, internal links, unique page metadata, canonical URLs, XML sitemap, existing robots preferences, organization/person/page/service/breadcrumb structured data, and FAQ structured data matching the visible Market Intelligence, Audience Development, experiential and commercial-reference answers. No search or AI citation outcome is promised. There is no special AI-only text or hidden keyword list.

## Final launch checks

Use a Vercel preview before switching the production deployment. Confirm the homepage, universe, Market Intelligence, TikTok Shop, Audience Development, experiential, contact and For AI URLs open correctly. Check the animation on an actual phone and laptop; software-rendered browser checks do not establish device performance.

Send an intentional test inquiry through each hosted form and confirm that Kevin receives both the contact fields and the relevant decision brief. FormSubmit activation for the stable Vercel preview was confirmed by the owner on September 28, 2026. Inbox delivery has not yet been independently verified. The site displays a copyable email address as an alternative. With JavaScript, forms use the service’s AJAX endpoint and show success or error feedback on the page.

After publication, submit the updated sitemap in Google Search Console and verify the new pages can be indexed. Check that deployment protection or hosting rules do not block public crawlers. Search and AI visibility can be measured after discovery and recrawling; no visibility increase has been established yet.

## Editing

Edit the text directly in the relevant HTML file. The scene reads concepts from `#scene-concepts` and the 19 relationships from `#path-data`. The dedicated Universe page also renders every concept as ordinary HTML in `#concept-data`. Scene settings are near `const CONFIG`. The CSS variables at the start of each page control paper, ink and green. The review file contains all content in expandable sections. Keep published pages consistent if you change a shared statement.

## The visual metaphor

500 spheres on desktop / 300 on mobile. 167 have public concept labels; a limited set is visible at any moment. Most nodes are disconnected. Selected encounters bring two distinct nodes together, grow both, and activate a secondary pathway. Growth symbolizes commercial possibility, not a live metric, member directory or valuation. The homepage starts the scene automatically. Motion pauses offscreen and respects reduced-motion preferences. A static vector field and all ordinary page content remain if WebGL fails.

## Inquiry form

The existing FormSubmit endpoint is preserved: kevin@getworkfriends.co. A visitor with a decision brief can add further context without having to repeat the brief in a required text field. Decision answers stay in the browser until the visitor chooses to submit. If a visitor follows an on-site contact link after using a tree, a temporary session-storage handoff carries that brief to the contact form, where it is visible and removable. Submitting sends the inquiry fields and attached brief through FormSubmit; normal browser POST remains available without JavaScript. Automated verification intercepted submissions and simulated the response; no test inquiry was sent by the automated checks. Checks cover accepted, rejected and network-failure responses, retaining entered text after failure. Preview activation is confirmed. Verify actual inbox delivery and the form configuration on the final production domain before launch.

## Inquiry attribution

Each JavaScript-enhanced submission includes the landing-page path, inquiry-page path, external referrer hostname when supplied by the browser, and any incoming `utm_source`, `utm_medium`, `utm_campaign`, `utm_content` and `utm_term` values. These are held for the browser session and included with the visitor’s deliberate submission. A visitor can also select how they found Workfriends, their role and optional timing. Referrers are sometimes unavailable; an absent referrer does not prove a direct visit.

`wf-analytics.js` prepares Vercel page-view tracking for getworkfriends.co and www.getworkfriends.co. Local review and preview domains do not send analytics. Query strings and fragments are removed from page-view events; form details are not sent to Analytics. Enable Web Analytics in the Vercel project and redeploy before verifying collection in its dashboard. Dashboard activation and live analytics collection are not yet confirmed. See https://vercel.com/docs/analytics/quickstart.

The optional `bookingUrl` constant in `wf-contact.js` is empty until Kevin supplies his public scheduling URL. Once configured, the booking link appears only after the inquiry provider accepts the submission. There is no placeholder booking link on the public site.

The page emits a `wf-inquiry-submitted` browser event after the form provider reports acceptance. The event includes page, topic, audience and whether a brief was present; it omits the visitor’s name, email and message. This remains a local integration hook; custom events are not sent to an external collector. Provider acceptance is not proof of inbox delivery.

## Search and AI discovery

All fourteen canonical pages contain their useful text in the initial HTML. Internal links, page-specific titles and descriptions, structured business/service information, a sitemap and readable questions connect the offerings. The existing crawler permissions are preserved, including OAI-SearchBot. GPTBot training permissions and search discovery are separate settings; the existing preference has not been changed.

The Google guidance used for this implementation is [AI features and your website](https://developers.google.com/search/docs/appearance/ai-features). It emphasizes accessible text, internal links and normal search fundamentals; there is no special AI schema or text file required for inclusion. See also [OpenAI’s crawler documentation](https://developers.openai.com/api/docs/bots). The public content describes real scope and illustrated situations, without fabricated clients, testimonials or results.

After publishing, verify public access and inspect the sitemap in Search Console. Review incoming inquiries by role, problem and source, then record which became qualified opportunities and paid work. That is the measure of commercial progress. Search visibility, AI recommendations and revenue have not been measured for this unpublished build.

## Research handling

The public Market Intelligence page presents original Workfriends principles and recurring questions from the reviewed research corpus. It does not republish confidential client PDFs, unverified current metrics, internal operator judgments, private pricing, or third-party decks as Workfriends-authored work. Dated estimates and analogue forecasts are not represented as present market facts. Specific future public case studies need a current source window, metric definitions and publication clearance for any client information.

## Verification and performance

The scene uses pinned Three.js 0.180.0. Inter is embedded. The production folder needs no third-party runtime request for typography or WebGL. Browser checks cover interaction, semantic content, mobile layout, reduced motion, a failed WebGL load and decision branches. Software-rendered browser testing is not a real-device performance benchmark. Check the animation on your usual phone and laptop before changing node counts or pixel ratio.

For a local server: `python3 -m http.server 8000` from this folder, then open http://localhost:8000.

## Licenses

Three.js is MIT licensed. Inter is SIL Open Font License 1.1. See `assets/THREE-LICENSE.txt` and `assets/INTER-OFL.txt`.
