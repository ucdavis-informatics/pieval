'''
File containing column datatype definitions to support automated building of the
pieval database schema
string data = types.NVARCHAR(25)
date/time = types.DateTime()
numeric = types.DECIMAL(precision=8, scale=3)
'''
from sqlalchemy import types

# Destination Table Metadata
annotation_events_metadata = {
    'response_time': types.DateTime(),
    'project_name': types.NVARCHAR(100),
    'user_name': types.NVARCHAR(100),
    'user_ip': types.NVARCHAR(100),
    'example_id': types.DECIMAL(precision=3, scale=0),
    'response': types.NVARCHAR(500),
    'context_viewed': types.NVARCHAR(50)
}


project_classes_metadata = {
    'project_name': types.NVARCHAR(100),
    'class': types.NVARCHAR(100)
}


project_data_metadata = {
    'project_name': types.NVARCHAR(100),
    'example_id': types.DECIMAL(precision=3, scale=0),
    'source_id': types.NVARCHAR(50),
    'data': types.NVARCHAR(None),
    'data_ext': types.NVARCHAR(None),
    'prompt': types.NVARCHAR(1000),
}


project_users_metadata = {
    'project_name': types.NVARCHAR(100),
    'user_name': types.NVARCHAR(100),
}


projects_metadata = {
    'project_name': types.NVARCHAR(100),
    'project_description': types.NVARCHAR(100),
    'project_mode': types.NVARCHAR(50)
}

user_details_metadata = {
    'user_name': types.NVARCHAR(100),
    'print_name': types.NVARCHAR(100),
    'email': types.NVARCHAR(150)
}


# wrapping it all into a single iterable
table_dict = {
    'annotation_events': {'filename': 'annotation_events.csv', 'metadata': annotation_events_metadata},
    'project_classes': {'filename': 'project_classes.csv', 'metadata': project_classes_metadata},
    'project_data': {'filename': 'project_data.csv', 'metadata': project_data_metadata},
    'project_users': {'filename': 'project_users.csv', 'metadata': project_users_metadata},
    'projects': {'filename': 'projects.csv', 'metadata': projects_metadata},
    'user_details': {'filename': 'user_details.csv', 'metadata': user_details_metadata}
}
