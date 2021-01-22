
import re
import ldap
import smtplib
from email.message import EmailMessage
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

def parseUsername(userid):
                # UX34JQ@aau.dk
    if len(userid) == 5:
        return userid

    x = re.match("^(\S+)@\S+$", userid)
    if x:
        return x.group(1)

def ldapLookup(userid,key):
    l = ldap.initialize(config['LDAP']['LDAPHost'],bytes_mode=False)

    try:
        l.protocol_version = ldap.VERSION3
        l.set_option(ldap.OPT_REFERRALS, 0)
        l.simple_bind_s(config['LDAP']['LDAPServiceUser'],config['LDAP']['LDAPServicePassword'])
        base = config['LDAP']['LDAPBaseDN']
        criteria = "(&(objectClass=user)({}={}))".format(key,userid)
        attributes = ['mail']
        result = l.search_s(base, ldap.SCOPE_SUBTREE, criteria, attributes)
        results = [entry for dn, entry in result if isinstance(entry, dict)]
        if len(results) > 0:
            return results
        else:
            raise NameError('LDAP: UserNotFound')
    finally:
        l.unbind()

def LookupADUserEmail(userid):

    try:
        results = ldapLookup(userid,'aauAAUID')
        return results
    except NameError:
       pass

    try:
        results = ldapLookup(parseUsername(userid),'aauAAUID')
        return results
    except NameError:
        pass

    try:
        results = ldapLookup(userid,'sAMAccountName')
        return results
    except NameError:
       pass

    try:
        results = ldapLookup(parseUsername(userid),'sAMAccountName')
        return results
    except NameError:
        pass


def sendMail(to,subject,body):
    s = smtplib.SMTP(host=config['Mail']['SmtpServer'], port=config['Mail']['SmtpPort'])
    if config['Mail']['SmtpPort'] != 25:
        s.starttls()
    if config['Mail']['Username']:
        s.login(config['Mail']['Username'],config['Mail']['Password'])

    msg = EmailMessage()
    msg['From']=config['Mail']['MailFrom']
    msg['To']=to
    msg['Subject']=subject
    text = body

    msg.set_content(text)
    try:
        s.send_message(msg)
    except Exception as e:
        print("Sending mail failed: {}".format(e))


def SendMailToADUser(userid, subject, body):
    try:
        emails = LookupADUserEmail(userid)
        if emails is None:
            print("Warning! No emails found for user {}".format(userid))
            return

        for email in emails:
        #convert from bytestring to string
            mail = str(email['mail'][0],'utf-8')
            #Send email to user
            sendMail(mail,subject,body)
    except Exception as e:
        print("Exception: userid: ",userid," ", e.__class__, "occurred.")
        import pprint as pp
        pp.pprint(e)

