#######################################
#  Made by: Inbal Kahlon              #
#  Date: 07/02/2020                   #
#  Automation engineer interview task #
#######################################

import imaplib
import smtplib
import email
import os
import re
from email.message import EmailMessage


user = input("enter your email: ")
password = os.environ.get('DB_PASS')
imap_url = "imap.yourdomain.com"
sender = "email of the person you want to receive email from "
# Where you want your attachments to be saved (ensure this directory exists)
attachment_dir = "d:\\pycharm\\"
smtp_con = 'smtp.yourdomain.com'

# connecting to email
def auth(user,password,imap_url):
    con = imaplib.IMAP4_SSL(imap_url)
    con.login(user, password)
    return con
# TODO: needs more athurization for user email and password, needs another dunction to check all this parameters.

# search email ids from praticular email
def search_emails(key, value, con):
    result, data = con.search(None, key, '"{}"'.format(value))
    id_list = data[0].split()
    return id_list
# TODO: needs more checkings to handle cases when data don't come back.

# allows you to download attachments
def get_attachments(msg):
    for part in msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        fileName = part.get_filename()
        if bool(fileName):
            filePath = os.path.join(attachment_dir, fileName)
            with open(filePath,'wb') as f:
                f.write(part.get_payload(decode=True))
        return fileName
  # TODO: needs to check if files contain the same name, otherwise we might need to add a number so the os could save them.
    
 

# send email
def send_email(email, password, smtp, sender_email, body):
    msg = EmailMessage()
    msg['Subject'] = "message"
    msg['From'] = email
    msg['To'] = sender_email
    msg.set_content(body)
    with smtplib.SMTP_SSL(smtp, 465) as smtp:
        smtp.login(email, password)
        smtp.send_message(msg)


def main():
    # connecting to our email user
    connection = auth(user, password, imap_url)

    # getting all emails IDs sent from user in safebreach.com
    connection.select('INBOX')
    email_id_list = search_emails('FROM', sender, connection)

    # getting all emails to see everything inside each message later on (using fetch)
    for id in email_id_list:
        result2, email_data = connection.fetch(id, '(RFC822)')
        raw_email = email_data[0][1].decode('utf-8')
        email_message = email.message_from_string(raw_email)

        # get information about the email message
        print("From: " + email_message['From'])
        print("Subject: " + email_message['Subject'])
        print("Date: " + email_message['Date'])

        # see if banana is in mail
        match = re.search(r'.*banana*', raw_email, re.IGNORECASE)

        # if banana is in mail find out if there's an attachment and download it if not send email "attachment missing"
        if match:
            done = 'yes'
            print('match found for word ', match.group())
            match_file = re.search(r"\.txt", raw_email, re.IGNORECASE)
            if match_file:
                done = "yes"
                print("files exists, downloading file")
                # get the attachment download it and then send the content inside to sender
                # running the file and catching if there's an error and sending it back
                attachment = get_attachments(email_message)
                try:
                    with open(attachment_dir + attachment, "r") as file:
                        read_data = file.read()
                        print("sending file content to your email")
                        send_email(user, password, smtp_con, sender, read_data)
                        break
                except FileNotFoundError as error:
                    print('An exception occurred with opening your file, sending exception to your email: {}'.format(error))
                    send_email(user, password, smtp_con, sender, error)
                finally:
                    print("done")
            else:
                done = "no"
                print("attachment missing, message has been sent to: " + sender)
                attachment = "attachment missing"
                send_email(user, password, smtp_con, sender, attachment)
                print("done")
        # if banana is not in email send "invalid keyword"
        else:
            done = 'no'
            print('no match for "banana" found, message has been sent to: ' + sender)
            keyword = "invalid keyword"
            send_email(user, password, smtp_con, sender, keyword)
            print("done")



if __name__ == "__main__":
    main()
