# Payer Disclosure Sources

| File | Payer | Source URL | Retrieval Date |
|------|-------|-----------|----------------|
| blue_shield_ca_2025.pdf | Blue Shield of California | https://www.blueshieldca.com/providers/prior-auth-metrics | 2026-04 |
| healthnet_2025.pdf | Health Net | https://www.healthnet.com/portal/provider/content/prior-authorization/metrics.html | 2026-04 |
| sfph_2025.pdf | San Francisco Health Plan | https://www.sfhp.org/providers/prior-authorization/metrics | 2026-04 |
| wellcare_healthnet_2025.pdf | WellCare / Health Net (Centene) | https://www.wellcare.com/prior-authorization-metrics | 2026-04 |

## Manual download fallback

If `fetch_all()` returns 403/429 for a payer, download the PDF manually from the source URL above
and save it to this directory using the filename convention `{payer_key}_2025.pdf`.
The pipeline skips fetch if the file already exists on disk.
