# Changelog

## v1.3

- Removed embedded API credentials and added safe secret templates.
- Removed automatic destructive deduplication at application startup.
- Added password-protected deployment mode and complete logout cleanup.
- Enabled SQLite foreign-key enforcement and WAL mode.
- Made clean database initialization reproduce infrastructure columns.
- Separated Value–Risk priority from governance approval.
- Added deterministic feasibility and Value–Risk validation.
- Blocked governance approval when assessments are missing or a hard gate is active.
- Replaced free-text reviewer identity with the authenticated identity.
- Fixed Expert Advice role matching and Linux filename capitalization.
- Added separation of duties for the Business Leader role.
- Persisted stakeholder assignments.
- Implemented workflow, decision-rights, delivery-gate, and lifecycle-monitoring pages.
- Added LLM-run metadata storage.
- Reworked PDFs to generate in memory with escaped dynamic content.
- Added missing and bounded dependencies.
- Replaced outdated project documentation with an as-built README and deployment checklist.

## v1.3.1

- Added explicit application-root import resolution for Streamlit Cloud.
- Pinned cloud runtime to Python 3.12.
