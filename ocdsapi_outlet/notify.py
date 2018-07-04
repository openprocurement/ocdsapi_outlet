""" 
notify.py - notifications about dump progress
TODO: slack notifications
"""
import emails


SUBJECT = "OCDS Dump ready"
BASE_MESSAGE = '''
<html>
<body>
<h1> OCDS Dump {status} </h1>
<p> {body} </p>'
</body>
</html>
'''


class EmailNofification(object):
    """ Send message by email about dump status with summary info"""
    def __init__(self, ctx):
        self.logger = ctx.obj['logger']
        self.send_from = ctx.obj['send_from']
        self.host = ctx.obj['smtp_host']
        self.user = ctx.obj['smtp_user']
        self.password = ctx.obj['smtp_password']
        self.recepients = ctx.obj['recepients']

    def _prepare_email_successs(self, manifest):
        """ Create message with summary info about success dump """

    def _prepare_email_fail(self):
        """ Create message with errors descriptions fired up during dump """

    def prepare_email(self):
        """
        Generic prepare message
        Returns:
            email message
        """

    def send_mail(self, message):
        """ Sends message """
        self.logger.info("Sending notification")
        sent = message.send(
            to=self.recepients,
            smtp={
                'host': self.host,
                'user': self.user,
                'password': self.password,
            }
        )
        if sent.status_code == 250:
            self.logger.info("Sent email to {}".format(self.recepients))
        else:
            self.logger.error(
                "Message not delivered successsfully. Reason: {}".format(str(sent.error))
            )
