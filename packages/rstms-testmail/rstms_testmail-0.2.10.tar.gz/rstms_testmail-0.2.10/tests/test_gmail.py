import os

from rstms_testmail import gmail

TEST_FROM = os.environ["TESTMAIL_FROM"]
TEST_TO = os.environ["TESTMAIL_TO"]


def disable_test_gmail_init():
    server = gmail.Gmail()
    assert server


def disable_test_gmail_send():
    server = gmail.Gmail()
    ret = server.send(TEST_FROM, TEST_TO, "testmail_test", "testmail_message")
    assert ret
