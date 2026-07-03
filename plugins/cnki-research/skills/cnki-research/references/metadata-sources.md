# Metadata sources

## OpenAlex

Use `https://api.openalex.org/works` for broad scholarly discovery, citation counts, and open-access metadata.

Useful response fields:

- `id`
- `doi`
- `title`
- `publication_year`
- `publication_date`
- `authorships[].author.display_name`
- `primary_location.source.display_name`
- `primary_location.landing_page_url`
- `primary_location.pdf_url`
- `open_access.is_oa`
- `open_access.oa_url`
- `cited_by_count`
- `type`

OpenAlex is not CNKI. Its Chinese coverage and metadata completeness vary. Its citation count must be labeled “OpenAlex cited by,” not “CNKI citations.”

## Crossref

Use `https://api.crossref.org/works/{doi}` for DOI registration metadata and `https://api.crossref.org/works?query=...` for discovery. Crossref generally lacks CNKI-specific metrics and may not include abstracts or full-text links.

## Deduplication

1. Normalize DOI by removing `https://doi.org/`, lowercasing, and trimming whitespace.
2. If DOI is absent, normalize Unicode title text, collapse whitespace, lowercase Latin text, and compare title plus first author and year.
3. Retain source-specific citation counts separately.

## Privacy

API requests disclose the query or DOI to the external provider. Send only required search terms and identifiers. Do not include private notes, unpublished findings, personal data, or credentials.

