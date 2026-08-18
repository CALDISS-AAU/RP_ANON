cd '/work/MatiasKokholmAppel#3073/RP_ANON'

uv run -m Pipelines.Backend.main_pdf_redactor \
    --input "/work/RP_ANON/ANON/Data/unmarked/Underretning 04-12-2025_unmarked.pdf" \
    --output-dir "/work/MatiasKokholmAppel#3073/RP_ANON/Pipelines/Backend/Data/output" \
    --categories cpr case-id address \
    --replacement "[REDACTED]"