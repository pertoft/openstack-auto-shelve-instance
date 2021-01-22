#!/usr/bin/python3
# 2020-01-18 Per Abildgaard Toft <pto@netic.dk>
# Auto shelve instaces, when they are older than x days

from datetime import datetime,timedelta
import openstack
from openstack.config import loader
import configparser
import utility

config = configparser.ConfigParser()
config.read('/opt/openstack-auto-shelve-instance/config.ini')


#Read configuration file from clouds.yml
osconfig = loader.OpenStackConfig()
cloud = openstack.connect(cloud="default")


def sendNotifyMailAboutToExpire(server,retire_date):
    user = cloud.identity.find_user(server.user_id)
    subject = "CLAAUDIA: Your VM ({}) is Strato about to expire!".format(server.name)
    msg = """
    Hello Strato user {},

    Your VM/Instance "{}" running on CLAAUDIA Strato will expire on {} and will be will be turned off (shelved).

    If you still need it, you can unshelve the instance from OpenStack Horizon GUI.

    Best regards,
    The CLAAUDIA Team

    """.format(user.name,server.name,str(retire_date.date()))
    print ("Sending expirey warning to {} about server {} will expire on {}".format(user.name,server.name,str(retire_date.date())))
    utility.SendMailToADUser(user.name,subject,msg)

def sendNotifyMailHasExpire(server):
    user = cloud.identity.find_user(server.user_id)
    subject = "CLAAUDIA: Your VM ({}) is Strato about to expire!".format(server.name)
    msg = """
    Hello Strato user {},

    Your VM/Instance "{}" running on CLAAUDIA Strato has expired and has now been Shutdown (shelved).

    If you still need it, you can "unshelve" the instance from OpenStack Horizon GUI and it will run for another {} days.

    Best regards,
    The CLAAUDIA Team

    """.format(user.name,server,config['OpenStack']['retire_after_days'])
    print("Sending instance has expired notification to {} for server {}".format(user.name,server))
    utility.SendMailToADUser(user.name,subject,msg)

retire_date = datetime.now() + timedelta(days=int(config['OpenStack']['retire_after_days']))
safe_to_delete_date = datetime.now() + timedelta(days=int(config['OpenStack']['retire_safe_to_delete_days']))

for server in cloud.compute.servers(all_tenants=True,vm_state='ACTIVE'):
        #If do not retire is defioned, skip instance
        if "do_not_retire" in server.metadata.keys():
            continue

        #Do not process admins instances
        if server.user_id == "f454263d2c104fdca6d1373b8098b1fa":
            continue

        # Dont touch servers with tasks running
        if server.task_state != None:
            continue

        # Check if retirement date has passed
        if "retire_date" in server.metadata.keys():
            retire_date_parsed = datetime.strptime(server.metadata['retire_date'],"%Y-%m-%d %H:%M:%S.%f")
            retire_date_warn = retire_date_parsed - timedelta(days=int(config['OpenStack']['retire_warn_days_before']))

            #Check if we should send a warning mail about instance expirey
            if datetime.now().date() == retire_date_warn.date():
                sendNotifyMailAboutToExpire(server,retire_date_parsed)

            if datetime.now() < retire_date_parsed:
                pass
            else:
                if server.status != 'SHELVED_OFFLOADED':
                    #Stamp the instance metadata when it was retired, so it can be deleted later
                    cloud.compute.set_server_metadata(server.id,shelved_date=str(datetime.now()))
                    #Shelve an instance - Shuts down the instance, and stores it together with associated data and resources (a snapshot is taken if not volume backed). Anything in memory is lost.

                    try:
                        print("Shelving server [{}] with retire_date {}".format(server.name,retire_date))

                        cloud.compute.shelve_server(server.id)
                        #Delte restire_date from metadata when the server is shelved, if user unshelves it will be tagged again
                        cloud.compute.delete_server_metadata(server.id,['retire_date'])

                        #Notify user that the server has been retired
                        sendNotifyMailHasExpire(server)

                    except:
                        print("ERROR: Shelving filed for server {}".format(server.name))
                        import pprint as pp
                        pp.pprint(server)


        else:
        # Its a new instance, stamp a retirement date into metadata
            print("Found new instance, stamping [{}] with retire_date {}".format(server.name,retire_date))
            cloud.compute.set_server_metadata(server.id,retire_date=str(retire_date))

