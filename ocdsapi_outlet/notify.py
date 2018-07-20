""" 
notify.py - notifications about dump progress
TODO: slack notifications
"""
import logging
import emails
from prettytable import PrettyTable


SUBJECT = "OCDS Dump ready"
BASE_MESSAGE = '''
<html>
<body>
<h1> OCDS Dump {status} </h1>
<p>{body}</p>'
</body>
</html>
'''


class EmailNofification(object):
    """ Send message by email about dump status with summary info"""
    def __init__(self, ctx):
        self.logger = ctx['logger']
        self.send_from = ctx['send_from']
        self.host = ctx['smtp_host']
        self.user = ctx['smtp_user']
        self.port = ctx['smtp_port']
        self.password = ctx['smtp_password']
        self.recepients = ctx['recepients']

    def _prepare_email_successs(self, manifest):
        """ Create message with summary info about success dump """
        table = PrettyTable()
        table.field_names = ['status', 'packages_count', 'zip_url']
        table.add_row(
            ['ok', len(manifest.releases), manifest.archive]
        )
        print(table.get_html_string())
        return BASE_MESSAGE.format(status='ok', body=table.get_html_string())

    def _prepare_email_fail(self):
        """ Create message with errors descriptions fired up during dump """
        return BASE_MESSAGE.format(status="fail", body="failed")

    def prepare_email(self, cfg):
        """
        Generic prepare message
        Returns:
            email message
        """
        if hasattr(cfg, 'manifest'):
            body = self._prepare_email_successs(cfg.manifest)
        else:
            body = self._prepare_email_fail()
        return emails.html(
            html=body,
            subject=SUBJECT,
            mail_from=self.send_from
        )

    def send_mail(self, cfg):
        """ Sends message """
        self.logger.info("Sending notification")
        message = self.prepare_email(cfg)
        sent = message.send(
            to=self.recepients,
            smtp={
                'host': self.host,
                'user': self.user,
                "port": self.port,
                'password': self.password,
                'tls': True,
                'timeout': 25
            },
        )
        if sent.status_code == 250:
            self.logger.info("Sent email to {}".format(self.recepients))
        else:
            self.logger.error(
                "Message not delivered successsfully. Reason: {}".format(sent.error)
            )
