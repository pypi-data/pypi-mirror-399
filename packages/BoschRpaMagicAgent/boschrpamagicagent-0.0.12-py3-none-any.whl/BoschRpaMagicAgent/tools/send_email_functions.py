import logging
import os
import re
import smtplib
import traceback
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from browser_use import ActionResult


def _json_dumps(payload: dict) -> str:
    """Serialize a small JSON string for LLM tool chaining."""
    # Avoid importing json if you prefer; but json is standard.
    import json
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def _parse_email_recipients(recipients: "str | list[str] | None") -> list[str]:
    """Parse recipients from string/list into a clean list of emails.

    Supports separators: comma, semicolon, whitespace, newline.
    """
    if recipients is None:
        return []
    if isinstance(recipients, list):
        raw = recipients
    else:
        raw = re.split(r"[,\s;]+", str(recipients).strip())
    cleaned = []
    for item in raw:
        email = (item or "").strip()
        if not email:
            continue
        cleaned.append(email)
    # Deduplicate while preserving order
    seen = set()
    result = []
    for email in cleaned:
        if email not in seen:
            seen.add(email)
            result.append(email)
    return result


def _validate_attachment_paths(attachment_file_paths: "list[str] | None") -> tuple[list[str], list[str], list[str]]:
    """Validate attachment paths.

    Returns:
        (valid_paths, missing_paths, non_absolute_paths)
    """
    attachment_file_paths = attachment_file_paths or []
    valid_paths = []
    missing_paths = []
    non_absolute_paths = []

    for path in attachment_file_paths:
        if not path:
            continue
        normalized_path = os.path.normpath(str(path).strip())
        if not os.path.isabs(normalized_path):
            non_absolute_paths.append(normalized_path)
            continue
        if not os.path.exists(normalized_path):
            missing_paths.append(normalized_path)
            continue
        valid_paths.append(normalized_path)

    return valid_paths, missing_paths, non_absolute_paths


def send_email_via_smtp_server(
    nt_account: str,
    nt_account_password: str,
    sender_email_address: str,
    sender_display_name: str,
    email_subject: str,
    email_body_html: str,
    to_recipients: "str | list[str]",
    cc_recipients: "str | list[str] | None" = None,
    attachment_file_paths: "list[str] | None" = None,
    smtp_server_host: str = "rb-smtp-auth.rbesz01.com",
    smtp_server_port: int = 25,
    smtp_use_starttls: bool = True,
) -> ActionResult:
    """Send an email via a corporate SMTP server (STARTTLS + NT authentication).

    This tool returns a structured JSON result so the LLM/Agent can reliably:
      - confirm who received the email
      - confirm which attachments were included
      - diagnose why sending failed (auth/connection/invalid recipients/etc.)

    Args:
        nt_account: NT account name (without domain), e.g. "LVZHC3".
        nt_account_password: Password (or app password) for NT authentication.
        sender_email_address: Sender email address, e.g. "xxx@cn.bosch.com".
        sender_display_name: Display name shown in the email client, e.g. "OIS2 AI BOT".
        email_subject: Email subject text.
        email_body_html: Email body in HTML format.
        to_recipients: Recipients in "a@x.com,b@y.com" or list form.
        cc_recipients: CC recipients in string or list form.
        attachment_file_paths: A list of ABSOLUTE local file paths to attach.
        smtp_server_host: SMTP host address.
        smtp_server_port: SMTP port, default 25.
        smtp_use_starttls: Whether to use STARTTLS.

    Returns:
        ActionResult.extracted_content JSON fields:
            - status: "ok" or "error"
            - smtp_server_host, smtp_server_port, starttls
            - to_recipients, cc_recipients (lists)
            - attachment_added, attachment_missing, attachment_not_absolute
            - error_type, error_message (on failure)
    """
    smtp_client = None

    # Bosch NT format (you had APAC\\{nt_account})
    smtp_username = f"APAC\\{nt_account}"

    to_list = _parse_email_recipients(to_recipients)
    cc_list = _parse_email_recipients(cc_recipients)

    valid_attachments, missing_attachments, non_absolute_attachments = _validate_attachment_paths(attachment_file_paths)

    # Fast input checks (helps LLM quickly self-correct)
    if not to_list and not cc_list:
        return ActionResult(
            extracted_content=_json_dumps({
                "status": "error",
                "operation": "send_email_via_smtp_server",
                "error_type": "no_recipients",
                "error_message": "Both to_recipients and cc_recipients are empty.",
            }),
            long_term_memory="Email sending blocked: no recipients."
        )

    try:
        smtp_client = smtplib.SMTP(smtp_server_host, smtp_server_port, timeout=30)

        if smtp_use_starttls:
            smtp_client.starttls()

        smtp_client.login(smtp_username, nt_account_password)

        # Build MIME message
        message = MIMEMultipart()
        # Include both display name and email address (more standard)
        message["From"] = Header(f"{sender_display_name} <{sender_email_address}>", "utf-8")
        message["To"] = ", ".join(to_list)
        if cc_list:
            message["Cc"] = ", ".join(cc_list)
        message["Subject"] = Header(str(email_subject), "utf-8")

        # Body (HTML)
        body_part = MIMEText(str(email_body_html), "html", "utf-8")
        message.attach(body_part)

        # Attachments
        attachment_added = []
        for file_path in valid_attachments:
            try:
                with open(file_path, "rb") as file_handle:
                    attachment_bytes = file_handle.read()

                attachment_part = MIMEApplication(attachment_bytes)
                file_name = os.path.basename(file_path)
                attachment_part.add_header("Content-Disposition", "attachment", filename=file_name)
                message.attach(attachment_part)
                attachment_added.append(file_path)
            except Exception:
                # If attachment read fails, treat it as missing/failed
                missing_attachments.append(file_path)

        all_recipients = to_list + cc_list

        smtp_client.sendmail(
            from_addr=sender_email_address,
            to_addrs=all_recipients,
            msg=message.as_string(),
        )

        logging.info("Email sent successfully.")

        return ActionResult(
            extracted_content=_json_dumps({
                "status": "ok",
                "operation": "send_email_via_smtp_server",
                "smtp_server_host": smtp_server_host,
                "smtp_server_port": smtp_server_port,
                "starttls": smtp_use_starttls,
                "sender_email_address": sender_email_address,
                "sender_display_name": sender_display_name,
                "to_recipients": to_list,
                "cc_recipients": cc_list,
                "to_count": len(to_list),
                "cc_count": len(cc_list),
                "attachment_added": attachment_added,
                "attachment_missing": missing_attachments,
                "attachment_not_absolute": non_absolute_attachments,
            }),
            long_term_memory=f"Email sent: to={len(to_list)}, cc={len(cc_list)}, attachments={len(attachment_added)}"
        )

    except smtplib.SMTPAuthenticationError as e:
        logging.info("Email sending failed (authentication).")
        return ActionResult(
            extracted_content=_json_dumps({
                "status": "error",
                "operation": "send_email_via_smtp_server",
                "error_type": "smtp_authentication_error",
                "error_message": str(e)[:300],
                "smtp_server_host": smtp_server_host,
                "smtp_server_port": smtp_server_port,
            }),
            long_term_memory="Email failed: SMTP authentication error."
        )

    except (smtplib.SMTPConnectError, OSError) as e:
        logging.info("Email sending failed (connection).")
        return ActionResult(
            extracted_content=_json_dumps({
                "status": "error",
                "operation": "send_email_via_smtp_server",
                "error_type": "smtp_connection_error",
                "error_message": str(e)[:300],
                "smtp_server_host": smtp_server_host,
                "smtp_server_port": smtp_server_port,
            }),
            long_term_memory="Email failed: SMTP connection error."
        )

    except smtplib.SMTPException as e:
        logging.info("Email sending failed (SMTP).")
        return ActionResult(
            extracted_content=_json_dumps({
                "status": "error",
                "operation": "send_email_via_smtp_server",
                "error_type": "smtp_error",
                "error_message": str(e)[:300],
            }),
            long_term_memory="Email failed: SMTP error."
        )

    except Exception as e:
        logging.info(f"Email sending failed.\n{traceback.format_exc()}")
        return ActionResult(
            extracted_content=_json_dumps({
                "status": "error",
                "operation": "send_email_via_smtp_server",
                "error_type": "unknown",
                "error_message": str(e)[:300],
            }),
            long_term_memory="Email failed: unknown error."
        )

    finally:
        if smtp_client is not None:
            try:
                smtp_client.quit()
            except Exception:
                pass
