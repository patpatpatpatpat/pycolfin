import re


def validate_user_id(user_id):
    """
    Raise an exception if the user_id does not follow the correct format.
    """
    invalid_user_id_msg = 'Invalid User ID. Please use a dash (-). Example: 1234-4567'
    user_id_pattern = re.compile('(\d{4}-\d{4})')

    if not user_id_pattern.match(user_id):
        raise Exception(invalid_user_id_msg)
