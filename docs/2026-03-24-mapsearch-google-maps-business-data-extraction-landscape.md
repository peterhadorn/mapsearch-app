# MapSearch.app Research: Google Maps Business Data Extraction SaaS Landscape

Date: March 24, 2026

## Executive Summary

MapSearch.app should not position as "another scraper." That lane is crowded and commoditized. The best opening is a productized, design-led "business search workspace" for non-technical operators who want Google Maps data fast, filter it visually, validate it before paying, and push it into outbound workflows.

Three market truths stand out:

1. Raw Google Maps data is cheap at the infrastructure layer.
   DataForSEO's current SERP pricing is usage-based, with Google Maps billed by returned-result blocks rather than expensive seat licenses. In practice, the infrastructure cost floor is low enough that product, workflow, and trust drive willingness to pay more than raw data access does. Sources: [DataForSEO SERP pricing](https://dataforseo.com/apis/serp-api/pricing), [DataForSEO pricing notes on Google Maps depth/billing](https://dataforseo.com/help-center/above-100-results-with-serp-api), [DataForSEO SERP API pricing reference](https://dataforseo.com/pricing/serp/serp-api).

2. The market splits into four distinct product shapes.
   - Cheap data utility: Outscraper, Bright Data dataset/API, many Apify actors
   - Lead-gen operator suite: MapLeads, D7 Lead Finder
   - Automation platform: PhantomBuster, Apify platform
   - Managed/enterprise data service: ScrapeHero, Bright Data enterprise

3. The UX gap is still real.
   Most tools either feel developer-first, workflow-first, or direct-response-marketing-first. Very few give users a clean, modern map-plus-table, pre-pay preview, strong filtering, and obvious unit economics. That is the clearest wedge for MapSearch.app.

For pricing strategy, the most relevant comparison set is the usage-based / non-lock-in cohort:

- Bright Data
- Outscraper
- Apify
- ScrapeHero
- MapsLeads

These are the closest comps for buyers who do not want to be forced into a pure monthly seat subscription.

## Competitive Snapshot

| Competitor | Current public pricing | Free tier / trial | Product shape | Best fit | Main weakness |
|---|---:|---|---|---|---|
| Outscraper | Google Search/Maps style pricing model with free tier, then $5/1,000 searches and $3/1,000 at higher volume on comparable Google search tier pages; prepaid/postpaid credits | Free tier on product pricing pages | Cheap cloud scraping utility | price-sensitive operators, agencies, builders | utilitarian UI, billing anxiety, less premium product feel |
| MapLeads | `Starter $97`, `Growth $147`, `Scale $197` monthly | No obvious free plan on pricing section; month-to-month language on site | Lead-gen app with outreach add-ons | agencies, local lead sellers, consultants | expensive effective per-result pricing, low independent review footprint |
| PhantomBuster | Free trial; `Start $56/mo`, `Grow $128/mo`, `Scale $352/mo` on annual billing | 14-day trial, no credit card | Automation platform | growth teams already doing multistep workflows | learning curve, account/platform-risk concerns, not maps-native |
| D7 Lead Finder | `Starter $21.99`, `Agency $42.99`, `Professional $89.99` monthly | No free plan found; month-to-month | Flat-rate lead finder | budget operators and list builders | dated UX, mixed data-quality perception |
| Bright Data | Google Maps dataset starts at up to ` $0.0025 / record`, min order ` $250` | Free trial exists at company level; dataset still has minimum order | Dataset/API + enterprise data infra | large teams, compliance-heavy buyers | high-friction for SMBs, enterprise feel |
| Apify | Platform has free start/no credit card; Google Maps actors vary; one current actor advertises ` $3.20 / 1,000 stores` + optional reviews/images | free start, many actors with trials | actor marketplace / scraping platform | technical teams, ops-heavy agencies | pricing predictability and actor-quality variance |
| ScrapeHero | Google Maps scraper page: `Free`, `Intro $5/mo`; full-service scraping starts at ` $550` one-off or ` $199/mo` | 400 free credits on marketplace page | self-serve + managed scraping | teams wanting support and scheduled jobs | less opinionated product UX, split between marketplace and services |
| MapsLeads | `Free`, `Starter $32/mo`, `Professional $79/mo`, `Business $159/mo`, `Enterprise $320/mo` | Free plan with 100 places/mo | modern niche maps lead-gen SaaS | SMBs/agencies who want map + filters | lower brand trust / smaller footprint |

Note on MapLeads pricing: the public page uses image-based pricing cards. Prices above were recovered from the publicly served card images using local OCR against those assets.

## Review Platform Audit: Trustpilot + G2

This matters because review-signal asymmetry is one of the easiest trust wedges for MapSearch.app.

| Competitor | Trustpilot | G2 | Read on what that means |
|---|---|---|---|
| Outscraper | `4.7/5`, `224 reviews` | `4.9/5`, `4 reviews` | broad public trust, very thin B2B marketplace proof |
| PhantomBuster | `3.5/5`, `109 reviews` | `4.4/5`, `138 reviews` | solid B2B credibility, softer public sentiment |
| Bright Data | `4.5/5`, `951 reviews` | `4.7/5`, `301 reviews` | strongest overall review moat in this set |
| Apify | `4.8/5`, `415 reviews` | `4.7/5`, `415 reviews` | unusually balanced review strength |
| ScrapeHero | no public Trustpilot profile found in this pass | `4.7/5`, `63 reviews` | respectable G2 proof, limited broader public-review presence |
| D7 Lead Finder | no public Trustpilot profile found in this pass | `3.7/5`, `5 reviews` | weak buyer-proof footprint |
| MapLeads / MapLeadsPro | no public Trustpilot profile found in this pass | no public G2 product profile found in this pass | trust gap for higher-ticket buyers |
| MapsLeads | no public Trustpilot profile found in this pass | seller profile visible, `0 reviews` | concept validated, trust not built yet |

Key implication:

- If MapSearch.app builds both `G2` and `Trustpilot` early, it can out-trust Outscraper with relatively modest review volume.
- Outscraper's vulnerability is not usage. It is weak `G2` depth.
- PhantomBuster has the opposite issue: stronger B2B proof than general public sentiment.

## 1. Competitor Analysis

### Outscraper

#### Pricing

- Official pricing page uses usage tiers instead of seat plans.
- Google-oriented search pricing on the live page shows:
  - Free tier before 10 searches
  - Medium tier: `$5 / 1,000 searches`
  - Business tier: `$3 / 1,000 searches`
- Billing model also supports prepaid credits and postpaid card billing.
- Sources: [Outscraper pricing](https://outscraper.com/pricing/), [Outscraper product page](https://outscraper.com/google-maps-scraper/).

#### Data returned

- Official product positioning emphasizes Google Maps business extraction plus enrichment.
- Public product copy highlights names, phone numbers, address, website, rating, review count, opening hours, place links, coordinates, category, price range, and optional downstream contact/social enrichment.
- G2 snippets also mention category, email, full address, latitude, longitude, source link, website.
- Sources: [Outscraper product page](https://outscraper.com/google-maps-scraper/), [G2 reviews snippet](https://www.g2.com/products/outscraper/reviews), [Trustpilot review page](https://www.trustpilot.com/review/outscraper.com).

#### UI/UX quality

- Functional rather than aspirational.
- Strength: clear console, lots of options, flexible exports, strong support visibility.
- Weakness: looks like a power tool, not a premium workspace. Filtering and export are strong, but the overall feel is still "scraper dashboard."
- G2 review specifically says the UI "could be more refined."

#### Free tier

- Trustpilot users explicitly mention successful use of the free tier.
- Official pricing includes free usage thresholds by product.
- Source: [Trustpilot Outscraper page](https://www.trustpilot.com/review/outscraper.com), [Outscraper pricing](https://outscraper.com/pricing/).

#### Target audience

- Agencies, local SEO operators, list builders, automators, and developers.
- Broad enough to serve both no-code and API users.

#### Strengths

- Aggressive price-to-output ratio.
- Large field set plus enrichments.
- Strong support reputation.
- Flexible exports and API access.

#### Weaknesses

- Less polished UX.
- Users report confusion around billing/credit usage.
- Preview/trust layer is weaker than a premium productized workflow.
- Not differentiated on design.

#### User complaints and sentiment

- Trustpilot: `224 reviews`, `4.7/5`, with AI summary noting ease of use and strong support, but also some billing and responsiveness complaints.
- G2: `4 reviews`, `4.9/5`. Positive but strategically weak as marketplace proof.
- Negative Trustpilot examples include surprise charges, "scam" allegations, and poor relevance on some runs.
- AppSumo complaint history includes requests for clearer credit usage notifications, better duplicate prevention, and closed-business handling.
- Reddit comparison thread shows buyers actively benchmark Outscraper on cost per result against Bright Data and email verification costs.
- Sources: [Trustpilot Outscraper](https://www.trustpilot.com/review/outscraper.com), [G2 Outscraper](https://www.g2.com/products/outscraper/reviews), [AppSumo review](https://appsumo.com/products/google-maps-scraper-by-outscraper/reviews/do-not-fall-for-this-scam-314284/), [Reddit alternatives thread](https://www.reddit.com/r/automation/comments/1nmtoe0/alternatives_to_outscraper_for_google_maps/).

#### Distribution and growth

- Strong SEO footprint.
- Semrush US snapshot: `8,427` organic keywords, `11,544` estimated organic traffic.
- Top US keywords include `outscraper`, `web scraping`, and `google maps scraper`.
- Likely acquisition mix: SEO, free-tier product-led growth, affiliate/referral trust loops, community word of mouth.
- Sources: Semrush `domain_ranks` and `domain_organic` for `outscraper.com`; [Trustpilot Outscraper](https://www.trustpilot.com/review/outscraper.com).

### MapLeads / MapLeadsPro

#### Pricing

- Public pricing cards show:
  - `Starter $97/month`
  - `Growth $147/month`
  - `Scale $197/month`
- Credits included:
  - Starter: `1,000` business search result credits / month
  - Growth: `2,000`
  - Scale: `3,000`
- FAQ states extra postcard credits start at `$2` each and AI site-builder credits start at `$1` each.
- Search result credits are use-it-or-lose-it monthly; bulk credits roll over.
- Source: [MapLeads public page](https://get.mapleads.io/).

#### Data returned / workflow

- Business search result credits are per business found.
- Site copy emphasizes business search, business emails, CRM import, AI route planner, AI sales trainer, power dialer snapshot, postcards, AI website mockups, and AI voice demo pages.
- Emails discovered for a business are included without extra per-email charge.
- This is not just data extraction. It is positioned as an operator toolkit for local-agency prospecting.
- Source: [MapLeads public page](https://get.mapleads.io/).

#### UI/UX quality

- Marketing site looks polished in a direct-response / GoHighLevel-funnel way, but not especially product-native.
- Pricing cards are image-based rather than structured HTML, which hurts transparency and trust.
- The product pitch is aggressive and ROI-first, less "beautiful data workspace," more "close prospects fast."

#### Free tier

- I did not find a public free tier or free trial on the main public pricing section.
- Public site emphasizes month-to-month billing and pay-as-you-go add-ons instead.

#### Target audience

- Local marketing agencies, freelancers, "rank-and-rent" style operators, sales teams doing local prospecting, coaches and agency owners.

#### Strengths

- Bundles data with activation: CRM import, postcards, AI site mockups, voice demos.
- Strong direct-response angle.
- Can justify higher ARPU than pure scraping utilities because it sells "closed business," not just rows.

#### Weaknesses

- Effective cost per included business result is high:
  - Starter: about `$0.097` per included result
  - Growth: about `$0.0735`
  - Scale: about `$0.0657`
- Review footprint is thin relative to price.
- Pricing transparency is weaker than best-in-class SaaS norms.
- Design feel is sales-funnel-heavy, not product-led or analyst-friendly.

#### User complaints and sentiment

- Trustpilot / G2 note: I did not find a public Trustpilot profile or a public G2 product review profile in this pass.
- Independent public review footprint appears limited compared with larger competitors.
- That lack of third-party proof is itself a weakness for higher-ticket SMB buyers.
- Public page source identifies the site as an affiliate-led funnel and prominently features agency-coach branding, which suggests a partner/referral-heavy acquisition motion rather than broad organic trust accumulation.
- Source: [MapLeads public page](https://get.mapleads.io/).

#### Distribution and growth

- Likely acquisition channels: affiliates, coaching ecosystems, agency communities, webinars/demo video, direct-response landing pages.
- Semrush US visibility for `mapleads.io` appears tiny: about `7` ranking keywords and about `37` estimated organic visits in the US snapshot.
- This suggests that SEO is not currently the engine.
- Sources: Semrush `domain_ranks` for `mapleads.io`, [MapLeads public page](https://get.mapleads.io/).

### PhantomBuster

#### Pricing

- Current official annual-billing pricing page shows:
  - Trial: `Free`
  - Start: `$56/month`, `$672 billed annually`
  - Grow: `$128/month`, `$1,536 billed annually`
  - Scale: `$352/month`, `$4,224 billed annually`
- Trial includes 5 automation slots, 2h execution time, 50 email credits, 1k AI credits, 100 URL finder credits, exports limited to 10 rows.
- Official page also states `14-day free trial`, no credit card required.
- Source: [PhantomBuster pricing](https://phantombuster.com/pricing).

#### Data returned / Google Maps coverage

- Google Maps Search Export returns name, category, rating, review count, attributes, address, Plus Code, status, website URL, phone number, opening hours, and optionally GPS coordinates.
- It does not return full individual reviews.
- Google Maps Search to Contact Data workflow adds title, place URL, website, status, subtitle, rating, review count, category, address, phone number, search query, and email.
- Google Maps extraction is capped by Google Maps limits, usually about `120-200` results per query.
- Sources: [Google Maps Search Export help](https://support.phantombuster.com/hc/en-us/articles/26971122390674-How-to-use-the-Google-Maps-Search-Export), [Google Maps Search to Contact Data help](https://support.phantombuster.com/hc/en-us/articles/26971113168146-How-to-use-the-Google-Maps-Search-to-Contact-Data).

#### UI/UX quality

- Best marketing UX in the category.
- Clean, modern, credible SaaS presentation with strong onboarding framing.
- Actual product interaction is workflow-first, not table/map-first. It feels like an automation workbench.
- Great if the buyer thinks in workflows; weaker if the buyer wants an exploratory business-search UI.

#### Free tier

- 14-day trial, no credit card.
- Export capped to 10 rows on free/free-trial.
- CSV upload and JSON exports restricted on free/free-trial for Maps automations.
- Sources: [PhantomBuster pricing](https://phantombuster.com/pricing), [Google Maps Search Export help](https://support.phantombuster.com/hc/en-us/articles/26971122390674-How-to-use-the-Google-Maps-Search-Export).

#### Target audience

- Growth teams, outbound teams, automation-first agencies, and technical operators who already use multi-step workflows.

#### Strengths

- Polished brand and onboarding.
- Strong automation abstraction.
- Broad ecosystem, integrations, and platform depth.
- Good credibility and social proof.

#### Weaknesses

- Not a purpose-built maps product.
- Buyers pay for slots/execution/credits, not straightforward "business result" pricing.
- Platform and account-risk concerns are material, especially for LinkedIn-centered users.
- Can be overkill for "I just want local businesses in a clean table."

#### User complaints and sentiment

- Trustpilot: `3.5/5`, `109 reviews`, with a very heavy `32%` 1-star share.
- G2: `4.4/5`, `138 reviews`, with recurring complaints around pricing, support, and complexity.
- Software Advice summary: `4.5/5` overall rating across `64` results, with customer support `4.1`, ease of use `4.3`; cons mention unfinished areas, need for extra tools/paid enrichments, and platform-risk concerns.
- Reddit thread: "steep learning curve, expensive, customer support is slow."
- Other Reddit threads emphasize LinkedIn safety risk, rate limits, and account-throttling concerns.
- Sources: [Trustpilot PhantomBuster](https://www.trustpilot.com/review/phantombuster.com), [G2 PhantomBuster](https://www.g2.com/products/phantombuster/reviews), [Software Advice PhantomBuster reviews](https://www.softwareadvice.com/data-extraction/phantombuster-profile/reviews/), [Reddit mixed-results thread](https://www.reddit.com/r/linkedinautomation/comments/1nf4cfe/3_months_with_phantombuster_mixed_results/), [Reddit safety thread](https://www.reddit.com/r/b2bmarketing/comments/1njhyto/phantombuster_still_safe_and_effective_for/), [Reddit PPC thread](https://www.reddit.com/r/PPC/comments/1rq6zrf/has_anyone_had_any_success_with_phatombuster/).

#### Distribution and growth

- Strong SEO plus YouTube/tutorial-led acquisition, plus affiliate program.
- Semrush US snapshot: about `17,289` organic keywords and `32,210` estimated organic visits.
- Top keywords are heavily branded plus adjacent automation use cases; that implies strong category memory and broad educational content.
- Official site also links tutorial videos and affiliate program directly.
- Sources: Semrush `domain_ranks` and `domain_organic` for `phantombuster.com`; [PhantomBuster pricing](https://phantombuster.com/pricing).

### D7 Lead Finder

#### Pricing

- Current public plan page shows:
  - Starter: `$21.99`
  - Agency: `$42.99`
  - Professional: `$89.99`
- Plan limits:
  - Starter: `12` daily searches, about `5,000` daily leads
  - Agency: `35` daily searches, about `12,000` daily leads
  - Professional: `120` daily searches, about `50,000` daily leads
- Month-to-month; no long-term commitment language is explicit.
- Source: [D7 plan page](https://d7leadfinder.com/auth/choose-plan/?perfectmoney=).

#### Data returned

- Base fields include emails / website URLs, address / telephone, social URLs.
- Higher plans add pixel detection, ad detection, reviews, business Google ranking, Instagram metrics, website scan data, bulk search/API, main category, domain/host info, and email provider name.
- Source: [D7 plan page](https://d7leadfinder.com/auth/choose-plan/?perfectmoney=).

#### UI/UX quality

- Effective but visibly old-school.
- Feels like a simple lead-finder utility from an earlier SaaS era.
- Low design trust compared with modern SaaS.

#### Free tier

- I did not find a public free plan or free trial on the current plan page.
- Public copy emphasizes month-to-month cancellation.

#### Target audience

- Budget-conscious agencies, local lead gen shops, freelancers, and cold-email operators who care more about volume than polished UX.

#### Strengths

- Very aggressive flat monthly pricing.
- Richer-than-expected feature set for the price.
- Attractive for power users who can amortize the subscription over high output.

#### Weaknesses

- Dated UI and brand perception.
- Data quality concerns appear recurrent in community discussions.
- Less premium, less trustworthy for higher-value buyers.

#### User complaints and sentiment

- Trustpilot note: I did not find a public Trustpilot profile in this pass.
- G2: `3.7/5`, `5 reviews`, which is too light to carry real buyer trust.
- Reddit mentions D7 as "costly for low-quality data" in one cold-email tooling thread, and other comments ask whether the data feels out of date.
- Sources: [Reddit cold email system thread](https://www.reddit.com/r/coldemail/comments/1q6cbjk/cold_email_system/), [Reddit accuracy thread](https://www.reddit.com/r/coldemail/comments/1jf1sc0/most_accurate_cold_email_sources/), [G2 result](https://www.g2.com/fr/products/d7-lead-finder/reviews).

#### Distribution and growth

- Semrush US snapshot: about `24,697` organic keywords and `4,173` estimated organic visits.
- Top traffic is mostly branded plus generic "lead finder" terms.
- Likely channels: SEO, affiliate/blog mentions, forum recommendations, long-tail lead-gen content.
- Sources: Semrush `domain_ranks` and `domain_organic` for `d7leadfinder.com`.

### Bright Data

#### Pricing

- Google Maps dataset page currently lists:
  - `191.5M+` records
  - starts at `up to $0.0025 per record`
  - minimum order ` $250`
- Refresh purchase options explicitly show one-time, biannual, quarterly, monthly with savings claims.
- Corporate site also pushes free-trial CTAs, but the dataset itself is not positioned like a frictionless SMB trial.
- Sources: [Bright Data Google Maps dataset](https://brightdata.com/products/datasets/google-maps).

#### Data returned

- Dataset page lists business names, addresses, contact details, ratings, reviews, place IDs, opening hours, URLs, and more.
- Review dataset includes review text, photos, reviewer profiles, engagement metrics.
- Delivery formats include JSON, NDJSON, JSON Lines, CSV, and Parquet.
- Source: [Bright Data Google Maps dataset](https://brightdata.com/products/datasets/google-maps).

#### UI/UX quality

- Very polished enterprise UX.
- Strong trust signals, documentation, delivery options, and configurability.
- But it is still an enterprise data procurement experience, not a search-and-workbench product for SMB operators.

#### Free tier

- Company-wide free-trial CTA exists.
- Dataset economics still include minimum order and procurement friction.

#### Target audience

- Enterprises, high-volume data teams, compliance-sensitive buyers, AI/data infrastructure teams.

#### Strengths

- Scale, compliance story, output formats, support, refresh subscriptions, delivery tooling.
- Good fit for structured data procurement and enterprise integrations.

#### Weaknesses

- Overbuilt for SMBs.
- Higher procedural friction.
- Less exploratory; more "buy dataset" than "work the leads now."

#### User complaints and sentiment

- G2: `301 reviews`, `4.7/5`, strong praise for support and setup.
- Trustpilot: `951 reviews`, `4.5/5`, with repeated praise for support and proxy reliability.
- Negative Trustpilot examples focus on expense, opaque infrastructure, strict onboarding/KYC, account flagging, and "black box" concerns.
- G2 dislike snippets include extra hoops for access to some resources and documentation clarity gaps.
- Sources: [G2 Bright Data reviews](https://www.g2.com/products/bright-data/reviews), [Trustpilot Bright Data](https://www.trustpilot.com/review/brightdata.com).

#### Distribution and growth

- Strongest content/distribution machine in the set.
- Semrush US snapshot: about `28,922` organic keywords and `76,723` estimated organic visits.
- Top ranking terms include branded queries plus broad proxy/web-scraping educational content.
- Acquisition channels appear to include SEO, webinars, partners, affiliates, enterprise sales, and thought leadership.
- Sources: Semrush `domain_ranks` and `domain_organic` for `brightdata.com`; [Bright Data dataset page](https://brightdata.com/products/datasets/google-maps).

### Apify

#### Pricing

- Platform pricing page markets "Start free (no credit card)."
- Pricing is mixed: platform usage plus actor-specific pricing.
- Google Maps actor pricing varies. One currently indexed actor, `agentx/google-maps-store-scraper`, advertises:
  - `$3.20 per 1,000 stores`
  - optional reviews at `$0.20 / 1,000`
  - optional images at `$0.20 / 1,000`
- Sources: [Apify pricing](https://apify.com/pricing), [Google Maps Store Scraper actor](https://apify.com/agentx/google-maps-store-scraper).

#### Data returned

- Actor example exposes 30+ fields, including name, category, address, area, coordinates, city/county/state/country, phone, website, menu URL, emails, social media, opening hours, popular times, about/amenities, related links, price range, rating, rating counts, review count, review tags, reviews, photos, and prices.
- Source: [Google Maps Store Scraper actor](https://apify.com/agentx/google-maps-store-scraper).

#### UI/UX quality

- Excellent for technical users, middling for non-technical buyers.
- Store and docs are strong, but actor comparison and cost predictability remain weak.
- Feels like an ecosystem, not a single simple product.

#### Free tier

- Official pricing page says start free with no credit card.
- Many actors also have short free trials or limited free usage.

#### Target audience

- Developers, technical agencies, ops teams, data engineers, automation-heavy businesses.

#### Strengths

- Breadth of actor ecosystem.
- Strong scheduling, proxy handling, exports, API access, and integration friendliness.
- Useful when your team wants optionality beyond Google Maps.

#### Weaknesses

- Actor quality varies.
- Pricing can be hard to predict.
- Harder for non-technical teams to compare options and know what they will really pay.
- Trust/risk depends on the actor maintainer.

#### User complaints and sentiment

- Trustpilot: `4.8/5`, `415 reviews`, very strong public sentiment overall.
- G2: `4.7/5`, `415 reviews`, strong praise for actor ecosystem and infrastructure.
- G2 complaint snippet: credit-based pricing can be hard to predict at scale; steep learning curve for non-technical users.
- Reddit complaint threads mention pricing changes, hard-to-compare actor search results, actors getting removed, and uneven reliability.
- TrustRadius shows `230` reviews and positive notes on reliability for recurring production pipelines.
- Sources: [Trustpilot Apify](https://www.trustpilot.com/review/apify.com), [G2 Apify reviews](https://www.g2.com/products/apify/reviews), [TrustRadius Apify](https://www.trustradius.com/products/apify/reviews), [Reddit pricing complaint](https://www.reddit.com/r/apify/comments/1rpswcb/apify_your_pricing_changes_for_builders_is_unfair/), [Reddit search-results complaint](https://www.reddit.com/r/apify/comments/1rh9dd1/the_actors_search_results_page_sucks_for/), [Reddit actor-removal discussion](https://www.reddit.com/r/coldemail/comments/1no75op/apify_apollo_scraper_removed_any_alternatives/).

#### Distribution and growth

- Strong SEO, docs, community, partner, and marketplace flywheel.
- Semrush US snapshot: about `58,490` organic keywords and `63,039` estimated organic visits.
- Top terms are branded and broad web-scraping education terms.
- Acquisition clearly includes SEO, docs, Discord/community, affiliate program, and builder ecosystem.
- Sources: Semrush `domain_ranks` and `domain_organic` for `apify.com`; [Apify pricing](https://apify.com/pricing).

### ScrapeHero

#### Pricing

- Marketplace page for Google Maps scraper shows:
  - Free: `400` data credits
  - Intro: `$5/month`, `4,500` data credits
- Company-wide full-service pricing starts at:
  - On-demand: `$550`
  - Business: `$199/month`
  - Enterprise Basic: `$1,500/month`
  - Enterprise Premium: `$8,000/month`
- Sources: [ScrapeHero Google Maps scraper marketplace page](https://www.scrapehero.com/marketplace/google-maps-search-results/), [ScrapeHero pricing](https://www.scrapehero.com/pricing/).

#### Data returned

- Public sample fields include name, address, phone, status, rating, reviews, website, Google CID, latitude, longitude, Google FID, keyword, timing, category, price range, result type, place ID, reviews link, URL, listing URL.
- Social and extra contact details are positioned as a second-step enrichment product.
- Source: [ScrapeHero Google Maps scraper marketplace page](https://www.scrapehero.com/marketplace/google-maps-search-results/).

#### UI/UX quality

- Functional and clearer than many scraper tools.
- More polished than D7, less elegant than PhantomBuster.
- Marketplace UX is solid but still utilitarian. The managed-service side feels separate from the self-serve flow.

#### Free tier

- Explicit free plan with `400` data credits and no credit card on the marketplace page.

#### Target audience

- Analysts, e-commerce/data teams, agencies, and buyers who may later need custom managed scraping.

#### Strengths

- Strong sample-data transparency.
- Clear scheduled-delivery story.
- Good bridge between self-serve and managed service.

#### Weaknesses

- Product identity is split between cloud marketplace and services firm.
- Less purpose-built for lead-generation UX than MapSearch.app could be.

#### User complaints and sentiment

- Trustpilot note: I did not find a public Trustpilot profile for ScrapeHero in this pass.
- G2: `4.7/5`, `63 reviews`.
- Official marketplace page highlights strong third-party ratings:
  - G2 `4.7`
  - Capterra `4.7`
  - Software Advice `4.7`
- Main likely friction is not bad reviews but product shape: it is still more "scraper marketplace / managed data vendor" than "lead-search workspace."
- Sources: [ScrapeHero Google Maps scraper marketplace page](https://www.scrapehero.com/marketplace/google-maps-search-results/), [Capterra ScrapeHero reviews](https://www.capterra.com/p/152963/ScrapeHero/reviews/), [G2 ScrapeHero reviews](https://www.g2.com/products/scrapehero/reviews).

#### Distribution and growth

- Very strong SEO via store-location and dataset pages.
- Semrush US snapshot: about `156,869` organic keywords and `157,420` estimated organic visits.
- Much of the SEO footprint comes from long-tail location-report pages and brand-location data demand.
- Sources: Semrush `domain_ranks` and `domain_organic` for `scrapehero.com`.

### Other Significant Player: MapsLeads

This one matters because it gets closer than most competitors to the actual MapSearch.app product shape.

#### Why it matters

- It explicitly claims:
  - advanced filters
  - grouping/merging datasets
  - "View Data on Map"
  - lower per-result costs
- It is one of the few visible products positioning around map + filtering + analysis, not just scraping.

#### Pricing

- Free: up to `100` places/month
- Starter: `$32/month`
- Professional: `$79/month`
- Business: `$159/month`
- Enterprise: `$320/month`
- Site also explicitly claims data cost per result of `$0.00325 or less`, and contact details cost per result of `$0.00180 or less`.
- Source: [MapsLeads](https://www.maps-leads.com/).

#### Takeaway

- MapsLeads validates the UX thesis, but its brand footprint, trust layer, and product proof are still small enough that a more premium, credible, and better-designed entrant can still win.
- Review note: I did not find a public Trustpilot profile in this pass. A G2 seller page is visible but currently shows `0 reviews`.

## 2. Market Pricing Research

### Usage-Based League Only

If MapSearch.app is competing in the usage-based / non-subscription-first lane, the two most important reference competitors are:

1. `Bright Data` for scale, enterprise trust, and dataset economics
2. `Outscraper` for direct self-serve Google Maps overlap

`Apify` matters as an ecosystem benchmark, but its pricing is actor-specific and plan-tier-sensitive.
`MapsLeads` matters as a UX + per-result benchmark.
`ScrapeHero` matters less for clean record-level economics because its public self-serve pricing is denominated in data credits, not directly in records.

So the short answer is:

- if you mean biggest player in this usage-based league: `Bright Data`
- if you mean most direct self-serve Google Maps competitor to beat on product: `Outscraper`

### $100 Benchmark: How Many Records Does $100 Buy?

This is the cleanest apples-to-apples comparison I could make from current public pricing on March 24, 2026.

| Competitor | Public pricing unit | Public rate used | Approx. output for `$100` | Important caveat |
|---|---|---:|---:|---|
| Bright Data | per record | `$0.0025 / record` | `40,000 records` | current public minimum order is `$250`, so `$100` is hypothetical only |
| Outscraper | per Google Maps business record | `$3 / 1,000 records` | `33,333 records` | higher-volume tier drops to `$1 / 1,000` after `100k` businesses |
| Apify | per scraped place, actor-specific | `from $2.10 / 1,000 places` on maintained `compass/google-maps-extractor` | `47,619 places` | this is actor-specific and reflects higher plan-tier pricing, not a clean prepaid `$100` plan |
| Apify (base Google actor model) | per scraped place | `$4 / 1,000 places` base price on Apify Google Maps help article | `25,000 places` | additional filters, details, contacts, images, reviews, and run fees reduce this |
| MapsLeads | per result claim | `$0.00325 / result or less` | `30,769 results` | site claims "or less"; exact one-time checkout pricing was not publicly exposed in crawlable text |
| ScrapeHero | data credits, not records | `225,000 data credits` on `$100/mo` Standard plan | not directly computable from public docs | ScrapeHero says records-per-credit varies by crawler; some need multiple pages per record |

What this means:

- `Apify` can look cheapest on a headline maintained-actor basis, but it is not a clean single-number benchmark because plan tier and add-ons materially change the outcome.
- `Bright Data` is cheaper than `Outscraper` on raw record cost, but comes with a higher minimum order and a more enterprise procurement motion.
- `Outscraper` is more expensive than `Bright Data` on raw unit cost, but still cheap enough to dominate the self-serve SMB lane.
- `MapsLeads` is roughly in the same raw-per-result band as `Outscraper`, but wraps the data in a more productized UX story.
- `ScrapeHero` is hard to benchmark on per-record economics from public material because credits map to crawl effort, not a flat record count.

### What businesses pay per Google Maps lead

There is no single market price because vendors charge in different units, but the current public range looks like this:

- Data infrastructure / raw record pricing:
  - Bright Data dataset: up to `$0.0025 / record`
  - Apify Google Maps actor example: about `$0.0032 / store`
  - MapsLeads claim: about `$0.00325 / result`
- Workflow-bundled SaaS pricing:
  - MapLeads: effective included-result pricing between about `$0.0657` and `$0.097` per result before considering bundled outreach tools
  - PhantomBuster and D7 are not meaningfully priced per result; they are platform or subscription economics

My inference: the open-market price for a plain Google Maps business row is roughly `0.25c` to `0.35c` when sold as infrastructure, but `2c` to `10c+` when sold as a workflow product with UX, enrichment, or outreach framing.

### Standard pricing models

- Per result / per record
  - Bright Data dataset
  - many Apify actors
  - MapsLeads
- Per search / per request / credits
  - Outscraper
  - DataForSEO
- Subscription with bundled monthly usage
  - MapLeads
  - D7 Lead Finder
  - PhantomBuster
  - ScrapeHero marketplace
- Enterprise minimum / managed contract
  - Bright Data
  - ScrapeHero services

### Sweet spot by segment

- SMB / solo operator
  - Best price tolerance: about `$19-$79/month`
  - Best model: free plan or tiny trial, then simple monthly plan or transparent pay-as-you-go
  - Key need: avoid complexity, know cost before export
- Agency
  - Best price tolerance: about `$79-$199/month`
  - Best model: subscription plus usage, with workflow/export/CRM value
  - Key need: speed, repeatability, team use, filters, enrichment
- Enterprise / data team
  - Best price tolerance: `$250+` minimums are acceptable if compliance and scale are real
  - Best model: per-record procurement or managed service with SLA/compliance

### How DataForSEO compares

- DataForSEO remains meaningfully below most end-user SaaS pricing when measured as raw data cost.
- Against infrastructure competitors:
  - close to Bright Data's dataset floor
  - lower than many self-serve actor/result products once UI and support markup is added
- Against workflow SaaS:
  - dramatically cheaper

That means MapSearch.app does not need a thin markup. It can price around product value, not API cost.

Practical implication:

- If MapSearch.app charges around `$0.005-$0.01` per exported result equivalent, it still has healthy room over infrastructure cost while remaining obviously cheaper than bundled agency-targeted products like MapLeads.
- Inside the usage-based league specifically, a practical message is:
  - cheaper and simpler than `Bright Data` for SMB workflows
  - better product and clearer than `Outscraper`
  - less confusing than `Apify`

## 3. UX / Product Research

### Which tools have the best UI/UX?

#### Best marketing UX

- PhantomBuster
  - Most polished brand, strongest onboarding story, modern SaaS trust layer.

#### Best enterprise trust UX

- Bright Data
  - Most complete enterprise experience, docs, formats, compliance signals, support framing.

#### Best "cheap utility" UX

- Outscraper
  - Not beautiful, but clear enough and operationally efficient.

#### Best "closest to MapSearch thesis"

- MapsLeads
  - Explicit map viewing, in-product filtering, grouping/merging, result-level economics.

#### Weakest UX

- D7 Lead Finder
  - Old-fashioned design and lower trust.

### Do any combine live map view with data tables?

- Yes, but only partially.
- MapsLeads explicitly claims "View Data on Map."
- PhantomBuster can extract coordinates but is not a spatial analysis UI.
- ScrapeHero and Outscraper expose coordinates/data, but their experience is still export-first.
- The market leader set still does not have a clearly dominant, beautiful, map-plus-table business-search product.

### What users wish existed but the market still under-serves

1. A genuinely premium table + map workspace for Google Maps business data.
2. Strong pre-search filters so users do not pay for junk.
3. Better previewing before payment/export.
4. Transparent, intuitive pricing tied to businesses found, not obscure credits/execution minutes.
5. Reliable outreach handoff after search without needing multiple tools.
6. Duplicate prevention, closed-business filtering, and cleaner relevance controls.
7. Better actor/tool comparison in marketplaces like Apify.

### Common complaints across the category

- Pricing unpredictability
- Surprise charges / credit burn
- Learning curve for non-technical buyers
- Data quality inconsistency
- Need for extra enrichment or export tools
- Weak trust / sparse independent reviews for smaller tools
- Platform/account-risk concerns for automation tools
- Too many steps between search and actual outreach

### How the better tools handle filtering, export, preview, and trials

- Filtering
  - Best: MapsLeads, Bright Data subsetting, Apify actor configurability
  - Weakest: older flat utilities or workflow tools that push filtering downstream
- Export
  - Most tools support CSV/JSON; Bright Data also adds Parquet/NDJSON and cloud delivery
- Preview
  - Usually weak
  - Free/trial rows are the dominant preview mechanism, not true "see everything, unlock export" UX
- Trials
  - Good: PhantomBuster, Apify, ScrapeHero, Outscraper free usage
  - Weak/unclear: MapLeads, D7

## 4. Distribution & Growth

### Observed acquisition patterns

- SEO is dominant for Outscraper, Bright Data, Apify, ScrapeHero.
- Tutorial/video-driven acquisition is strong for PhantomBuster and likely for many automation tools.
- Affiliate/partner ecosystems are visible for PhantomBuster, Apify, Bright Data, and likely central for MapLeads.
- Community/Reddit/forum word of mouth remains important in this category because buyers compare data quality and cost in public threads.

### Semrush US snapshot

| Domain | Organic keywords | Est. organic traffic | Notes |
|---|---:|---:|---|
| `scrapehero.com` | 156,869 | 157,420 | huge long-tail SEO machine |
| `brightdata.com` | 28,922 | 76,723 | strong enterprise + education content |
| `apify.com` | 58,490 | 63,039 | ecosystem/docs/store flywheel |
| `phantombuster.com` | 17,289 | 32,210 | strong branded + automation content |
| `outscraper.com` | 8,427 | 11,544 | niche SEO but meaningful |
| `d7leadfinder.com` | 24,697 | 4,173 | brand plus generic lead-finder terms |
| `mapleads.io` | 7 | 37 | tiny SEO footprint; likely non-SEO acquisition |

Inference: MapSearch.app does not need to out-SEO Bright Data or Apify immediately. It needs to own a narrower intent cluster first:

- `google maps lead search`
- `google maps business database`
- `google maps businesses export`
- `find businesses by keyword + radius`
- `google maps leads with website filter`

### Revenue visibility

- Public revenue is not disclosed for the major players in the sources reviewed.
- Best available public operating signals:
  - Bright Data: `20,000+ customers`
  - PhantomBuster: `100,000+ professionals`, `2.5M+ satisfied users since 2016`
  - Bright Data and Outscraper both show large review footprints
- I would not publish revenue estimates without stronger evidence.

## 5. Adjacent Opportunities

### Pingen.com direct-mail integration

Pingen is a strong adjacent fit.

- It provides an API for automated letter sending.
- Pricing is pay-per-letter with no setup fee, no monthly subscription, no minimum volumes.
- Public pricing shows processing/envelope, paper, print, and destination-delivery components.
- It supports API access, webhooks, track-and-trace, local printing, email-to-letter, S3/SFTP flows, and multi-user support.
- Sources: [Pingen pricing](https://www.pingen.com/en/prices/), [Pingen API](https://www.pingen.com/en/post-api/), [Pingen homepage](https://www.pingen.com/en/).

Why it matters for MapSearch.app:

- Most Google Maps data tools stop at export.
- Direct mail is a differentiated downstream action, especially for:
  - local agencies
  - home service outreach
  - reputation/rebuild offers
  - "no website" or "bad website" businesses

Strong product idea:

- Search businesses
- filter to no/weak website
- generate personalized postcard or letter
- send directly through Pingen

That is more differentiated than "CSV export" and avoids crowded email-only workflows.

### Tools that already combine data with outreach

- MapLeads
  - postcards, AI site mockups, CRM import, power dialer concepts
- PhantomBuster
  - CRM integrations, Zapier/Make/n8n workflows, outreach automations
- D7
  - positioned around lead list creation for email/phone/social outreach, but not deeply integrated UX

Gap:

- There is still no obvious category winner combining:
  - search
  - map/table analysis
  - enrichment
  - outbound execution
  - premium UX

### CRM integrations users are likely to expect

- HubSpot
- Pipedrive
- Close
- Salesforce
- Google Sheets
- CSV
- Zapier / Make / n8n
- Webhooks

For SMBs and agencies, Google Sheets and HubSpot matter first. For more technical buyers, webhooks and n8n matter next.

## 6. Positioning Recommendation for MapSearch.app

### Recommended positioning

Position MapSearch.app as:

> The cleanest way to search Google Maps business data, filter it visually, and turn it into outreach-ready lists.

Not:

- scraper platform
- data infrastructure
- automation engine

Yes:

- business search workspace
- local market prospecting tool
- map + table + export + outreach handoff

### The gap in the market

The gap is not "cheaper data."

The gap is:

1. Beautiful UX for non-technical users.
2. Live map + table exploration.
3. Clear filters before and after search.
4. Transparent unit economics.
5. Better trust than the small niche entrants.
6. Optional downstream outreach actions, especially direct mail and CRM push.

### What would make someone switch from Outscraper?

Outscraper buyers would switch if MapSearch.app gives them:

1. Better relevance and preview.
   Let them see what they are about to export, filter junk out, and understand why a result matches.

2. Better working UX.
   A serious table, saved views, map view, dedupe, instant field filtering, website-quality flags.

3. Simpler pricing.
   Charge per kept/exported business or via clean monthly bundles. Avoid scary credit-burn feelings.

4. Higher-trust activation workflow.
   CRM export, Google Sheets sync, direct mail, and maybe email-enrichment add-ons without needing a second tool chain.

5. Better operator features.
   Saved searches, presets by niche, "no website / bad website / low reviews / no recent posts" filters, territory splitting.

### Recommended product strategy

#### Core wedge

- Keyword + location + radius
- live table
- live map
- very fast filters
- export/pay per result

#### Immediate differentiators

- filter before search and after search
- visual map clustering
- clean pricing in plain English
- saved search presets
- website/no-website and weak-website scoring
- dedupe and blacklist management
- preview before purchase/export

#### Next differentiators

- direct mail via Pingen
- Google Sheets sync
- HubSpot / Pipedrive / Close
- website snapshot / tech-stack signals
- opportunity scoring for agencies

#### Avoid for the first iteration

- becoming a general-purpose scraping platform
- broad multi-network automations
- overly technical workflow builder

That would put MapSearch.app into direct competition with Apify and PhantomBuster, where they already have ecosystem advantages.

## Final Recommendation

MapSearch.app should compete on:

- product taste
- clarity
- speed to useful output
- operator workflow
- downstream activation

It should not try to compete on:

- cheapest raw row
- biggest automation marketplace
- enterprise procurement/compliance theater

The most promising practical angle is:

> "Find local businesses the way an agency actually works: search, filter, map, preview, export, and launch outreach in one place."

That is more concrete than "Google Maps scraper" and more differentiated than "lead finder."

## Outscraper Battlecard: How To Demolish Them

If Outscraper is the primary target, the strategy should be explicit.

### Where Outscraper is actually strong

- cheap and credible
- broad scraper catalog
- good support reputation
- strong Trustpilot proof
- power-user flexibility

Trying to beat them on "cheaper rows" is the wrong fight.

### Where Outscraper is vulnerable

1. Design and perceived product quality
   - even positive G2 feedback says the UI could be more refined
   - the experience feels like a scraping console, not a premium operator workspace

2. Buyer-proof asymmetry
   - Trustpilot is strong
   - G2 is tiny at `4 reviews`
   - MapSearch.app can plausibly out-trust Outscraper on G2 much faster than it can outspend them on SEO

3. Billing anxiety
   - public complaints repeatedly mention confusing billing, extra charges, and credit surprises

4. Weak activation layer
   - strong on extraction
   - weaker on "what do I do with these businesses next?"

5. Weak opinionated workflow
   - Outscraper gives data
   - it does not give a premium search -> qualify -> map -> export -> CRM / direct-mail motion

### How MapSearch.app should beat Outscraper

1. Win on the first 5 minutes
   - faster onboarding
   - better empty state
   - clear preview before pay/export
   - beautiful map + table from the first search

2. Make pricing legible
   - price per saved/exported business or simple monthly bundles
   - show running totals live
   - no opaque credit burn

3. Ship opinionated qualification filters
   - no website
   - weak website
   - rating / reviews thresholds
   - category / chain exclusion
   - duplicate suppression
   - closed / suspicious businesses

4. Own the downstream workflow
   - HubSpot / Sheets / Close export
   - direct mail via Pingen
   - saved searches and reusable lead presets

5. Build review moats early
   - get to `25-50` real G2 reviews quickly
   - build Trustpilot in parallel
   - use that to close the trust gap while Outscraper still looks under-reviewed on G2

The right message against Outscraper is:

> Outscraper is a capable scraper. MapSearch.app is the better product.

## Bright Data Battlecard: Why They Matter

If you are choosing only one "biggest player" in the usage-based league, it is `Bright Data`.

### Why Bright Data matters most

- biggest trust moat in this set
- strongest combined `Trustpilot + G2` footprint
- enterprise-grade brand
- cheapest publicly visible raw record economics among major branded players here
- strongest procurement story for large data buyers

### Why Bright Data is still not the whole market

- it is not the closest UX comp
- it is not the easiest self-serve SMB purchase
- it is more "buy data" than "work the market"

So the clean strategic framing is:

- `Bright Data` is the scale and pricing benchmark
- `Outscraper` is the direct self-serve product benchmark
- `MapSearch.app` should aim to feel better than both

## Source List

### Official product / pricing pages

- [Outscraper pricing](https://outscraper.com/pricing/)
- [Outscraper Google Maps scraper](https://outscraper.com/google-maps-scraper/)
- [MapLeads public site](https://get.mapleads.io/)
- [PhantomBuster pricing](https://phantombuster.com/pricing)
- [PhantomBuster Google Maps Search Export help](https://support.phantombuster.com/hc/en-us/articles/26971122390674-How-to-use-the-Google-Maps-Search-Export)
- [PhantomBuster Google Maps Search to Contact Data help](https://support.phantombuster.com/hc/en-us/articles/26971113168146-How-to-use-the-Google-Maps-Search-to-Contact-Data)
- [D7 Lead Finder plans](https://d7leadfinder.com/auth/choose-plan/?perfectmoney=)
- [Bright Data Google Maps dataset](https://brightdata.com/products/datasets/google-maps)
- [Apify pricing](https://apify.com/pricing)
- [Apify Google Maps Extractor](https://apify.com/compass/google-maps-extractor)
- [Apify Google Maps pricing help](https://help.apify.com/en/articles/10774732-google-maps-scraper-is-going-to-pay-per-event-pricing)
- [Apify Google Maps Store Scraper actor](https://apify.com/agentx/google-maps-store-scraper)
- [ScrapeHero pricing](https://www.scrapehero.com/pricing/)
- [ScrapeHero Google Maps scraper marketplace page](https://www.scrapehero.com/marketplace/google-maps-search-results/)
- [MapsLeads](https://www.maps-leads.com/)
- [Pingen pricing](https://www.pingen.com/en/prices/)
- [Pingen API](https://www.pingen.com/en/post-api/)

### Reviews / community / comparison signals

- [Trustpilot Outscraper](https://www.trustpilot.com/review/outscraper.com)
- [G2 Outscraper](https://www.g2.com/products/outscraper/reviews)
- [Trustpilot PhantomBuster](https://www.trustpilot.com/review/phantombuster.com)
- [G2 PhantomBuster](https://www.g2.com/products/phantombuster/reviews)
- [AppSumo Outscraper review](https://appsumo.com/products/google-maps-scraper-by-outscraper/reviews/do-not-fall-for-this-scam-314284/)
- [Reddit Outscraper alternatives thread](https://www.reddit.com/r/automation/comments/1nmtoe0/alternatives_to_outscraper_for_google_maps/)
- [Software Advice PhantomBuster reviews](https://www.softwareadvice.com/data-extraction/phantombuster-profile/reviews/)
- [Reddit PhantomBuster mixed-results thread](https://www.reddit.com/r/linkedinautomation/comments/1nf4cfe/3_months_with_phantombuster_mixed_results/)
- [Reddit PhantomBuster safety thread](https://www.reddit.com/r/b2bmarketing/comments/1njhyto/phantombuster_still_safe_and_effective_for/)
- [Reddit PhantomBuster PPC thread](https://www.reddit.com/r/PPC/comments/1rq6zrf/has_anyone_had_any_success_with_phatombuster/)
- [G2 D7 Lead Finder](https://www.g2.com/products/d7-lead-finder/reviews)
- [Reddit D7 thread](https://www.reddit.com/r/coldemail/comments/1q6cbjk/cold_email_system/)
- [Reddit D7 accuracy thread](https://www.reddit.com/r/coldemail/comments/1jf1sc0/most_accurate_cold_email_sources/)
- [G2 Bright Data](https://www.g2.com/products/bright-data/reviews)
- [Trustpilot Bright Data](https://www.trustpilot.com/review/brightdata.com)
- [Trustpilot Apify](https://www.trustpilot.com/review/apify.com)
- [G2 Apify](https://www.g2.com/products/apify/reviews)
- [TrustRadius Apify](https://www.trustradius.com/products/apify/reviews)
- [Reddit Apify pricing complaint](https://www.reddit.com/r/apify/comments/1rpswcb/apify_your_pricing_changes_for_builders_is_unfair/)
- [Reddit Apify actor-search complaint](https://www.reddit.com/r/apify/comments/1rh9dd1/the_actors_search_results_page_sucks_for/)
- [Reddit Apify actor removal thread](https://www.reddit.com/r/coldemail/comments/1no75op/apify_apollo_scraper_removed_any_alternatives/)
- [Capterra ScrapeHero reviews](https://www.capterra.com/p/152963/ScrapeHero/reviews/)
- [G2 ScrapeHero reviews](https://www.g2.com/products/scrapehero/reviews)

### DataForSEO pricing references

- [DataForSEO SERP API pricing](https://dataforseo.com/apis/serp-api/pricing)
- [DataForSEO result-depth / billing reference](https://dataforseo.com/help-center/above-100-results-with-serp-api)
- [DataForSEO SERP pricing reference](https://dataforseo.com/pricing/serp/serp-api)

### Traffic / keyword estimates

- Semrush `domain_ranks` and `domain_organic` snapshots for `outscraper.com`, `phantombuster.com`, `d7leadfinder.com`, `brightdata.com`, `apify.com`, `scrapehero.com`, and `mapleads.io` collected on March 24, 2026.
