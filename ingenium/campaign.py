"""Turn an Ingenium execute() report into real, usable campaign deliverables.

Everything here is generated locally from the report — no external services
are called and nothing is sent. The output is a folder of files a business
owner can actually use: a landing page, outreach email copy, a calendar file
for the follow-ups, an outreach CSV, and the raw JSON report.
"""
import csv
import html
import io
import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

FOLLOW_UP_DAYS = 3


def _first_offer(edge: dict) -> str:
    """Pull the first knowledge 'offers' entry, if any."""
    offers = edge.get("knowledge", {}).get("offers", [])
    return offers[0] if offers else ""


def landing_page_html(report: dict) -> str:
    """Render a standalone landing page for the objective.

    Args:
        report: An ``Ingenium.execute()`` report.

    Returns:
        A complete, self-contained HTML document as a string.
    """
    edge = report["edge"]
    objective = report["objective"]
    positioning = edge.get("strategy", {}).get("positioning", "")
    offer = _first_offer(edge)
    tone = ", ".join(edge.get("brand", {}).get("tone_words", []))

    esc = html.escape
    offer_block = f'<p class="offer">{esc(offer)}</p>' if offer else ""
    tone_note = f'<!-- brand tone: {esc(tone)} -->' if tone else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(objective)}</title>
{tone_note}
<style>
  body {{ font-family: -apple-system, Segoe UI, Roboto, sans-serif; margin: 0;
    color: #1a1d24; background: #f7f7f9; }}
  .hero {{ max-width: 720px; margin: 0 auto; padding: 4rem 1.5rem; text-align: center; }}
  h1 {{ font-size: 2.4rem; margin-bottom: .5rem; }}
  .sub {{ color: #5b6270; font-size: 1.1rem; }}
  .offer {{ display: inline-block; margin: 1.5rem 0; padding: .6rem 1rem;
    background: #eef; border-radius: 8px; font-weight: 600; }}
  .cta {{ display: inline-block; margin-top: 1rem; padding: .8rem 1.6rem;
    background: #5b5bf0; color: #fff; text-decoration: none; border-radius: 8px; }}
</style>
</head>
<body>
  <main class="hero">
    <h1>{esc(objective)}</h1>
    <p class="sub">{esc(positioning)}</p>
    {offer_block}
    <div><a class="cta" href="#contact">Get started</a></div>
  </main>
</body>
</html>
"""


def email_copy(report: dict, recipient: str) -> dict:
    """Draft an outreach email for one recipient.

    Args:
        report: An ``Ingenium.execute()`` report.
        recipient: The recipient's email address.

    Returns:
        Dict with ``to``, ``subject``, and ``body`` — ready to send.
    """
    edge = report["edge"]
    objective = report["objective"]
    positioning = edge.get("strategy", {}).get("positioning", "").strip()
    offer = _first_offer(edge)

    lines = [f"Hi there,", ""]
    hook = f"We're {positioning}. " if positioning else ""
    lines.append(f"{hook}{objective} — and we wanted you to be first to know.")
    if offer:
        lines += ["", f"This month: {offer}."]
    lines += ["", "Reply to this email or give us a call to lock it in.", "", "Talk soon,", "The team"]
    return {"to": recipient, "subject": objective, "body": "\n".join(lines)}


def _ics_escape(text: str) -> str:
    """Escape a value for an iCalendar text field."""
    return text.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def followups_ics(report: dict, start: datetime | None = None) -> str:
    """Build an iCalendar (.ics) document for the scheduled follow-ups.

    Args:
        report: An ``Ingenium.execute()`` report.
        start: Base time follow-ups are offset from (defaults to now, UTC).

    Returns:
        A VCALENDAR document as a string. One VEVENT per follow-up.
    """
    base = (start or datetime.now(timezone.utc)).astimezone(timezone.utc)
    when = base + timedelta(days=FOLLOW_UP_DAYS)
    stamp = base.strftime("%Y%m%dT%H%M%SZ")
    day = when.strftime("%Y%m%dT%H%M%SZ")
    objective = report["objective"]

    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Ingenium//Campaign//EN", "CALSCALE:GREGORIAN"]
    for i, event in enumerate(report["pipeline"]["follow_up"]["scheduled"], 1):
        attendee = event.get("attendees", [""])[0]
        lines += [
            "BEGIN:VEVENT",
            f"UID:ingenium-{stamp}-{i}@campaign",
            f"DTSTAMP:{stamp}",
            f"DTSTART:{day}",
            f"DURATION:PT30M",
            f"SUMMARY:{_ics_escape('Follow up: ' + objective)}",
            f"DESCRIPTION:{_ics_escape('Follow up with ' + attendee)}",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def outreach_csv(report: dict) -> str:
    """Build a CSV of everyone reached in this campaign.

    Args:
        report: An ``Ingenium.execute()`` report.

    Returns:
        CSV text with a header row and one row per outreach message.
    """
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["recipient", "objective", "subject", "status"])
    for message in report["pipeline"]["outreach"]["sent"]:
        writer.writerow([message["to"], report["objective"], message["subject"], "drafted"])
    return buffer.getvalue()


def _slug(text: str) -> str:
    return "".join(c if c.isalnum() else "-" for c in text.lower()).strip("-")[:60] or "campaign"


def export_campaign(report: dict, out_dir: str | Path, start: datetime | None = None) -> dict:
    """Write a full set of campaign deliverables to a directory.

    Args:
        report: An ``Ingenium.execute()`` report.
        out_dir: Destination directory (created if it does not exist).
        start: Base time for follow-up dates (defaults to now).

    Returns:
        Dict mapping a short artifact name to the Path written.
    """
    target = Path(out_dir)
    target.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}

    def _write(name: str, filename: str, content: str) -> None:
        path = target / filename
        path.write_text(content, encoding="utf-8")
        written[name] = path

    _write("landing", "landing.html", landing_page_html(report))
    _write("calendar", "followups.ics", followups_ics(report, start=start))
    _write("outreach", "outreach.csv", outreach_csv(report))
    _write("report", "report.json", json.dumps(report, indent=2))

    emails_dir = target / "emails"
    emails_dir.mkdir(exist_ok=True)
    for i, message in enumerate(report["pipeline"]["outreach"]["sent"], 1):
        email = email_copy(report, message["to"])
        path = emails_dir / f"{i:02d}-{_slug(email['to'])}.txt"
        path.write_text(f"To: {email['to']}\nSubject: {email['subject']}\n\n{email['body']}\n", encoding="utf-8")
        written[f"email_{i}"] = path

    logger.info("Exported %d campaign artifacts to %s", len(written), target)
    return written
