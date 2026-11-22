export default {
  "title": "Maple Hosting Index",
  "intro": "A dated sample of .ca domains, observed through DNS. Explore the networks and estimated countries behind their public addresses.",
  "eyebrow": "CANADIAN DOMAINS / NETWORK OBSERVATIONS",
  "accent": "#41614c",
  "tint": "#e4eee7",
  "method": [
    "The reproducible sample is the first 100 .ca apex domains by rank in the identified dated Tranco list. A .ca suffix does not prove Canadian ownership, and the sample is not a measure of all Canadian websites.",
    "A and AAAA answers come from Google DNS-over-HTTPS with EDNS client subnet disabled. Every returned public IP is associated with RIPE RIS origin-AS data and RIPEstat DB-IP Country Lite country estimates. Missing answers and unknown geography stay visible.",
    "An apex DNS answer is not proof of where the browser ultimately loads a website. Redirects, CDNs, anycast, resolver location and dynamic answers can all change the observation. IP geography is not evidence of data residency.",
    "Provider groups are labelled by origin ASN and published network holder. A known CDN-capable network does not prove that a particular domain uses its CDN service. Country/provider counts use distinct domains and can overlap."
  ],
  "id": "maplehosting",
  "explorer-title": "Follow the record.",
  "cadence": "Monthly automated collection. Source dates and capture dates are shown separately.",
  "facets": [
    {
      "key": "countries",
      "label": "Estimated country"
    },
    {
      "key": "networks",
      "label": "Origin network"
    },
    {
      "key": "ipv6",
      "label": "IPv6 answer"
    }
  ],
  "columns": [
    {
      "key": "domain",
      "label": "Domain"
    },
    {
      "key": "rank",
      "label": "Tranco rank"
    },
    {
      "key": "networks",
      "label": "Origin networks"
    },
    {
      "key": "countries",
      "label": "Estimated countries"
    },
    {
      "key": "ipv6",
      "label": "IPv6 answer"
    },
    {
      "key": "dns_status",
      "label": "DNS status"
    }
  ],
  "related": [
    {
      "label": "Hosted Where",
      "url": "https://coolcode.ca/hosted-where/"
    },
    {
      "label": "ASN Canada",
      "url": "https://coolcode.ca/asn-canada/"
    },
    {
      "label": "Boomerang Meter",
      "url": "https://coolcode.ca/boomerang-meter/"
    }
  ]
};
