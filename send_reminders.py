import pandas as pd
import logging
from app.data_loader import FileDataLoader, DBDataLoader
import instance.config as config
from smtplib import SMTP
from email.message import EmailMessage
import click

@click.command(name='send_reminders')
def send_reminders():
    """Build a logger"""
    logger = logging.getLogger(__name__)
    # formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    # logger.setLevel(logging.DEBUG)
    # ch = logging.StreamHandler()
    # ch.setFormatter(formatter)
    # logger.addHandler(ch)

    """Build datasource"""
    if config.DATASOURCE_TYPE == 'file':
        pv_dl = FileDataLoader(config.DATASOURCE_LOCATION, logger)
    elif config.DATASOURCE_TYPE == 'db':
        pv_dl = DBDataLoader(config.VAULT_TOKEN,
                             config.VAULT_SERVER,
                             config.DATASOURCE_LOCATION,
                             config.DB_SCHEMA,
                             logger)

    # get user data - this will limit to people who have been configured to receive alerts
    user_details = pv_dl.getUserData()
    # get project data (all projects)
    data = pv_dl.getProjectData(return_as_dataframe=True)
    for one_user in user_details:
        user_name = one_user.get('user_name')
        print_name = one_user.get('print_name')
        email = one_user.get('email')

        # get data for this user
        logger.info(f"Getting data for {user_name}")
        try:
            pieval_projects = pv_dl.getProjects(user_name=user_name, return_as_dataframe=True)
            logger.info(f"User has {pieval_projects.shape[0]} projects")
            prev_annots_for_user = pv_dl.getPriorAnnotations(user_name=user_name, return_as_dataframe=True)
            logger.info(f"User has {prev_annots_for_user.shape[0]} completed annotations")

            # group and join
            proj_example_counts = (data.groupby(['project_name'])
                                   .size()
                                   .to_frame()
                                   .rename(columns={0: 'num_examples'})
                                   .reset_index())

            user_proj_counts = (prev_annots_for_user.groupby(['project_name'])
                                .agg(
                num_annotated=('example_id', 'count'),
                last_annot_time=('response_time', 'max')
            )
                                .reset_index())
            user_proj_counts['days_since_last'] = (pd.datetime.now() - user_proj_counts['last_annot_time']).dt.days
            logger.info(user_proj_counts.head())

            proj_status = pd.merge(proj_example_counts,
                                   user_proj_counts,
                                   on='project_name',
                                   how='left')
            proj_status['pct_complete'] = round((proj_status['num_annotated'] / proj_status['num_examples']) * 100)
            proj_status = proj_status.fillna(0)
            pieval_projects = pieval_projects.merge(proj_status.filter(['project_name', 'pct_complete','days_since_last']),
                                                    on='project_name', how='left')
            prompts = (pieval_projects.loc[((pieval_projects['pct_complete'] < 100)
                                            &(pieval_projects['days_since_last'] >= config.DAYS_TILL_PROMPT))]
                                   .to_dict(orient='records'))

            logger.info(f"Current Username is {user_name}, print name is {print_name} and email is {email}")
            # print(incomplete_projects)
            if len(prompts) > 0:
                # build a status_string with N entries
                status_string = ''
                for ip in prompts:
                    status_string += f"""You are {ip.get('pct_complete')} percent complete \
on the {ip.get('project_name')} project\n"""

                # combine that into the message
                message = f"""Hi {print_name},\nThis is Pieval!  I'm reaching out because \
you have {len(prompts)} incomplete annotation projects \
and I would like to see you stay on top of the leaderboard!\n{status_string}\
Please login here to finish up: {config.HOST_FQDN + config.BLUEPRINT_URL_PREFIX}"""

                logger.info("===== SENDING EMAIL ==========")
                msg = EmailMessage()
                msg.set_content(message)
                msg['Subject'] = f'Pieval Annotation Reminder'
                msg['From'] = config.FROM_EMAIL
                msg['To'] = email

                if config.IGNORE_SEND:
                    logger.info("DRY RUN!! Printing to console, not sending emails")
                    print(message)
                else:
                    try:
                        with SMTP("smtp.ucdavis.edu", port=587) as smtp:
                            smtp.send_message(msg)
                            logger.info(f'Sent reminder email to: {email}')
                    except:
                        logger.error(f'Could not send email to {email}.')


        except KeyError as ke:
            logger.error("There is not data for this user!")
            logger.error(ke)

        print()


if __name__ == '__main__':
    send_reminders()