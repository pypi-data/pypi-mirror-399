import typing as t
import css_inline
from django.template import loader
from django.tasks import task, TaskResult
from django.core.mail import EmailMultiAlternatives
from saas_base.settings import saas_settings
from saas_base.signals import mail_queued


def send_template_email(
    template_id: str,
    subject: str,
    recipients: t.List[str],
    context: t.Dict[str, t.Any],
    from_email: t.Optional[str] = None,
    headers: t.Optional[t.Dict[str, str]] = None,
    reply_to: t.Optional[str] = None,
):
    if from_email is None:
        from_email = saas_settings.DEFAULT_FROM_EMAIL
    text_message, html_message = render_mail_messages(template_id, context)
    result: TaskResult = send_email.enqueue(
        subject=str(subject),
        recipients=recipients,
        text_message=text_message,
        html_message=html_message,
        from_email=from_email,
        headers=headers,
        reply_to=reply_to,
    )
    mail_queued.send(
        sender=None,
        template_id=template_id,
        **result.kwargs,
        result=result,
    )


@task
def send_email(
    subject: str,
    recipients: t.List[str],
    text_message: str,
    html_message: t.Optional[str] = None,
    from_email: t.Optional[str] = None,
    headers: t.Optional[t.Dict[str, str]] = None,
    reply_to: t.Optional[str] = None,
):
    mail = EmailMultiAlternatives(
        subject,
        body=text_message,
        from_email=from_email,
        to=recipients,
        headers=headers,
        reply_to=reply_to,
    )
    if html_message:
        mail.attach_alternative(html_message, 'text/html')

    return mail.send()


def render_mail_messages(template_id: str, context: t.Dict[str, t.Any]) -> t.Tuple[str, str]:
    context.setdefault('site', saas_settings.SITE)
    text: str = loader.render_to_string(f'saas_emails/{template_id}.text', context)
    html: str = loader.render_to_string(f'saas_emails/{template_id}.html', context)
    return text, css_inline.inline(html)
