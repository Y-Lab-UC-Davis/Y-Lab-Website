---
layout: page
title: Join the Lab
eyebrow: Get involved
prose: true
description: "How to join our research group: current openings for undergraduates, graduate students, and postdocs, and what to include when reaching out."
---

Thank you for your interest in joining our team!

Whether your background is in engineering, physical sciences, or related disciplines, we welcome motivated researchers to explore open questions with us.

{%- if site.assets.culture_photo and site.assets.culture_photo != "" %}
<figure class="culture-shot">
  <img src="{{ site.assets.culture_photo | relative_url }}" alt="Lab group" loading="lazy">
  <figcaption></figcaption>
</figure>
{% endif -%}

**What we look for:**

- **Curiosity and independence:** driving your own research project with guidance.
- **Willingness to grow:** developing both your technical depth and collaboration skills.
- **Care for the lab:** keeping our environment welcoming, safe, and rigorous.

New here? Our [research]({{ '/research/' | relative_url }}) page shows what our group works on.

## Openings

<div class="grid grid-3 openings">
{%- assign ug = site.data.openings.undergrad -%}
<div class="card">
{%- if ug.open %}<span class="status status--active">{{ ug.open_note }}</span>{% else %}<span class="status status--paused">{{ ug.closed_note }}</span>{% endif %}
<h3>Undergraduates</h3>
<p>{% if ug.open %}{{ ug.open_note }}{% else %}{{ ug.closed_note }}{% endif %}</p>
{%- if site.undergrad_form_url and site.undergrad_form_url != "" -%}
<a class="btn btn--primary" href="{{ site.undergrad_form_url }}" rel="noopener">Interest form &rarr;</a>
{%- else -%}
<a class="btn btn--primary" href="mailto:{{ site.lab.pi_email }}?subject={{ 'Prospective undergraduate researcher' | uri_escape }}&body={{ site.data.openings.email_body | uri_escape }}">Email PI &rarr;</a>
{%- endif -%}
</div>
{%- assign grad = site.data.openings.graduate -%}
<div class="card">
{%- if grad.open %}<span class="status status--active">Now recruiting</span>{% else %}<span class="status status--paused">Open via fellowship</span>{% endif %}
<h3>Graduate students</h3>
<p>{% if grad.open %}{{ grad.open_note }}{% else %}{{ grad.closed_note }}{% endif %}</p>
<a class="btn btn--primary" href="mailto:{{ site.lab.pi_email }}?subject={{ 'Prospective graduate applicant' | uri_escape }}&body={{ site.data.openings.email_body | uri_escape }}">Email PI &rarr;</a>
</div>
{%- assign postdoc = site.data.openings.postdoc -%}
<div class="card">
{%- if postdoc.open %}<span class="status status--active">Now recruiting</span>{% else %}<span class="status status--paused">Open via fellowship</span>{% endif %}
<h3>Postdocs</h3>
<p>{% if postdoc.open %}{{ postdoc.open_note }}{% else %}{{ postdoc.closed_note }}{% endif %}</p>
<a class="btn btn--primary" href="mailto:{{ site.lab.pi_email }}?subject={{ 'Prospective postdoc' | uri_escape }}&body={{ site.data.openings.email_body | uri_escape }}">Email PI &rarr;</a>
</div>
</div>

{%- if site.data.funding and site.data.funding.size > 0 -%}
<p class="muted u-fs-sm"><strong>Funding your own spot?</strong> Browse our <a href="{{ '/lab-guide/funding-applications/' | relative_url }}">curated list of fellowships &amp; scholarships</a>.</p>
{%- endif -%}

## What to include in a first email

A short, specific note helps us respond quickly:

- **Who you are:** program or year, and a line of background.
- **Why this lab:** a [project]({{ '/research/' | relative_url }}) or [paper]({{ '/publications/' | relative_url }}) of interest.
- **What you'd like to build or learn** here.
- **Your timing**, with a CV attached.

