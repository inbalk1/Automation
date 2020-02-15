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
password = input("password")
imap_url = "imap.yourdomain.com"
sender = "email of the person you want to receive email from "
# Where you want your attachments to be saved (ensure this directory exists)
attachment_dir = "d:\\pycharm\\"
smtp_con = 'smtp.yourdomain.com'

# connecting to email
def auth(user,password,imap_url):
    con = imaplib.IMAP4_SSL(imap_url)
    con.login(user, password)

# TODO: missing parameters checking.
    # try:
    #   con = imaplib.IMAP4_SSL(imap_url)
    #   con.login(user, password)
    # except (pass error, username error, con error):
    #   print("wrong credentials, please try again")
    #   con.login(user, password)
    # else:
    #    print("succsesfully logged in")
    # return con

# search email ids from praticular email
def search_emails(key, value, con):
    result, data = con.search(None, key, '"{}"'.format(value))
    id_list = data[0].split()
    return id_list

# TODO: missing parameters checking (checking the result variable).
    # result check (because it basically contains a value if the emails exits or not)

    # result, data = con.search(None, key, '"{}"'.format(value))
    # if result = "no":
    #   print("files doesn't exists, please try another key or email")
    # else:
    #   id_list = data[0].split()


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

# TODO: adding some counter to files (because if files have the same name they can't be saved so we need to add numbers).
# here i added counter to files and i added an extention checker (with mimetypes) instead of using regex later on.
    # import mimetypes
    # counter = 1
    # for part in email_message.walk():
    #     if part.get_content_maintype() == "multipart":
    #         continue
    #     if part.get('Content-Disposition') is None:
    #         continue
    #     filename = part.get_filename()
    #     ext = mimetypes.guess_extension(filename)
    #     if ext = ".txt":
    #         filename = 'msg-part-%08d%s' % (counter, ext)
    #     counter += 1
    # return file name

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