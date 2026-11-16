---
layout: page
title: Contact
eyebrow: Get in touch
prose: true
description: "Contact our research group about collaboration, media inquiries, or joining the lab."
---

<div class="contact-card">
<div class="contact-card__info">
<p class="contact-card__name">{{ site.lab.pi }}</p>
<p class="muted">Lab Director · {{ site.lab.institution }}</p>
<p><a href="mailto:{{ site.lab.pi_email }}">{{ site.lab.pi_email }}</a><br>
{{ site.lab.location }}</p>
</div>
<a class="btn btn--primary contact-card__btn" href="mailto:{{ site.lab.pi_email }}">Email the lab &rarr;</a>
</div>

## How to reach out

<div class="grid grid-2 u-mt-12">
<a class="card card--link" href="{{ '/join/' | relative_url }}">
<h3>Prospective students &amp; postdocs</h3>
<p>Start with the Join page that includes current openings, timing, and application details.</p>
</a>
<a class="card card--link" href="mailto:{{ site.lab.pi_email }}?subject={{ 'Press inquiry' | uri_escape }}">
<h3>Press &amp; media</h3>
<p>We're happy to talk about and share our work. Please reach out via email.</p>
</a>
<a class="card card--link" href="mailto:{{ site.lab.pi_email }}?subject={{ 'Research collaboration' | uri_escape }}">
<h3>Research collaboration</h3>
<p>Curious about working together or using research facilities? Please reach out via email.</p>
</a>
</div>

<p class="muted u-fs-sm u-mt-16">Find me online:
<a href="https://wzyan24.wixsite.com/wenzhong-yan" rel="noopener">personal website</a> ·
<a href="{{ site.lab.scholar }}" rel="noopener">Google Scholar</a> ·
<a href="https://orcid.org/{{ site.lab.orcid }}" rel="noopener">ORCID</a> ·
<a href="https://mae.ucdavis.edu/people/wenzhong-yan" rel="noopener">UC&nbsp;Davis MAE page</a>
{%- if site.lab.instagram and site.lab.instagram != "" %} · <a href="{{ site.lab.instagram }}" rel="noopener">Instagram</a>{% endif -%}
{%- if site.lab.linkedin and site.lab.linkedin != "" %} · <a href="{{ site.lab.linkedin }}" rel="noopener">LinkedIn</a>{% endif -%}
</p>
