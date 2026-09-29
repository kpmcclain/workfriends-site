# Workfriends

A static website. No build step, framework, database, account system or API key.

## Form endpoint configuration

This build uses **formspree** at `https://formspree.io/f/mvkglbdw`. The authoring source controls this in `wf-form-config.json`; rebuilding updates all three forms together. Formspree must use the exact `/f/` endpoint from the owner's verified account, never an email-address endpoint or a made-up form ID. Its free native flow uses Formspree's hosted confirmation page. A custom native return page is a paid Formspree setting; `_next` must not be sent as though it enables that feature. The `/thanks/` page remains available for a separately configured supported return flow. Keep the default provider spam checks enabled. The supplied Formspree endpoint is configured. A real preview Contact submission was accepted by Formspree and independently verified in the Workfriends inbox on September 29, 2026. Historical FormSubmit notes below describe the prior implementation.

## GitHub → Vercel

1. Unzip this folder. Put its **contents** at the root of your website repository: `index.html`, `assets`, `tiktok-shop`, `audience-development`, `experiential`, `contact`, `thanks`, `universe`, `market-intelligence`, the six commercial-page folders, `for-ai.html`, `404.html`, `robots.txt`, `sitemap.xml`, and `vercel.json`. Upload the complete contents together.
2. Commit the files to GitHub. Your existing Vercel integration can deploy them. For a new Vercel project, select **Other**, leave Build Command empty, and use the repository root as the output.
3. Keep your existing domain settings. The canonical URLs target https://www.getworkfriends.co. If you choose another canonical domain, replace it consistently in HTML, robots.txt and sitemap.xml.

`workfriends-universe.html` is the separate one-file review version. You can open it directly; its 3D engine needs an internet connection. Use this full folder for the production site: it includes Three.js locally and separates the reference pages into stable URLs.

## What is here

- Home: Workfriends positioning around creator-economy revenue, three commercial entry points, the founder story, a named Commercial Sprints offer and small links to both Decision Trees within the commerce-and-audience door. Kevin’s personal LinkedIn is linked from the founder story and shared footer. Inter, the single-color headline and The Universe are retained. The homepage starts the animated Universe automatically, with pause controls, reduced-motion support and a still fallback.
- `/universe/`: 167 readable concepts, 19 illustrative pathways and the interactive scene.
- `/tiktok-shop/`: the existing copy, a three-question decision brief with a direct skip to the inquiry form, and the existing inquiry form. Visitors contact Kevin for advice; the site does not generate a personalized recommendation.
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

A real Contact inquiry from the preview was accepted by Formspree and received in the Workfriends inbox at 2:17 p.m. America/Denver on September 29, 2026, including the full message and page context. All three forms also passed intercepted native-POST checks with and without JavaScript; those checks do not send emails. Formspree currently shows its hosted confirmation page. Keep the default provider security checks enabled. The site also displays a copyable email address. After production deployment, perform one deliberate delivered-inquiry smoke test from the final domain.

After publication, submit the updated sitemap in Google Search Console and verify the new pages can be indexed. Check that deployment protection or hosting rules do not block public crawlers. Search and AI visibility can be measured after discovery and recrawling; no visibility increase has been established yet.

## Editing

Edit the text directly in the relevant HTML file. The scene reads concepts from `#scene-concepts` and the 19 relationships from `#path-data`. The dedicated Universe page also renders every concept as ordinary HTML in `#concept-data`. Scene settings are near `const CONFIG`. The CSS variables at the start of each page control paper, ink and green. The review file contains all content in expandable sections. Keep published pages consistent if you change a shared statement.

## The visual metaphor

500 spheres on desktop / 300 on mobile. 167 have public concept labels; a limited set is visible at any moment. Most nodes are disconnected. Selected encounters bring two distinct nodes together, grow both, and activate a secondary pathway. Growth symbolizes commercial possibility, not a live metric, member directory or valuation. The homepage starts the scene automatically. Motion pauses offscreen and respects reduced-motion preferences. A static vector field and all ordinary page content remain if WebGL fails.

## Inquiry form

The existing FormSubmit endpoint is preserved: kevin@getworkfriends.co. A visitor with a decision brief can add further context without having to repeat the brief in a required text field. Decision answers stay in the browser until the visitor chooses to submit. If a visitor follows an on-site contact link after using a tree, a temporary session-storage handoff carries that brief to the contact form, where it is visible and removable. Submitting sends the inquiry fields and attached brief through the provider’s normal browser POST. The default security check remains enabled. The exact page URL is provided using the documented _url field, and _next is set to this deployment’s /thanks/ URL when JavaScript is available. Automated verification intercepts submissions; it does not prove actual inbox delivery. Preview activation is confirmed. Verify actual inbox delivery and the form configuration on the final production domain before launch.

## Unconfirmed delivery and recovery

On September 29 the owner’s second test confirmed that the AJAX request timed out. Fresh inbox delivery remains a launch gate. A read-only provider diagnostic from the execution environment was blocked; that does not establish the cause of the owner's browser failure. The AJAX transport has now been removed. Native submission lets the provider display any security check, rejection or confirmation directly. The script does not infer success from sending the request. On submission, a temporary draft is stored in the current browser tab and can be restored when returning to the form. It is cleared on the confirmation page or discarded after 30 minutes when the form is opened again. Recovery offers a complete email draft or a copyable inquiry, including long briefs. Nothing is sent automatically through the fallback. The confirmation page is excluded from the sitemap and marked noindex. Provider acceptance is not proof of inbox delivery.

## Inquiry attribution

Each JavaScript-enhanced submission includes the landing-page path, inquiry-page path, external referrer hostname when supplied by the browser, and any incoming `utm_source`, `utm_medium`, `utm_campaign`, `utm_content` and `utm_term` values. These are held for the browser session and included with the visitor’s deliberate submission. A visitor can also select how they found Workfriends, their role and optional timing. Referrers are sometimes unavailable; an absent referrer does not prove a direct visit.

`wf-analytics.js` adds Vercel page-view tracking to the Workfriends domains and this project's Vercel deployments. Local review does not send analytics. Query strings and fragments are removed from page-view events; form details are not sent to Analytics. Web Analytics was confirmed enabled in the Workfriends Vercel project on September 29, 2026. Use the dashboard's Production/Preview filter to separate launched-site traffic from review visits. Publishing this build is required before the production site uses the new integration. See https://vercel.com/docs/analytics/quickstart and https://vercel.com/docs/analytics/using-web-analytics.

The optional `bookingUrl` constant in `wf-contact.js` is empty until Kevin supplies his public scheduling URL. Once configured, the booking link appears on the /thanks/ page. There is no placeholder booking link on the public site. No custom form-conversion event is sent; /thanks/ page views are not proof of inbox delivery.

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
