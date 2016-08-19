
from passlib.apps import custom_app_context as pwd_context
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model

from ...common.abstract.models import AbstractBaseModel


class AbstractUser(AbstractBaseModel):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Username, password and email are required. Other fields are optional.
    """
    __abstract__ = True

    username = columns.Text(min_length=3, max_length=32, index=True, required=True)
    password = columns.Text(min_length=3, required=True)
    email = columns.Text(min_length=5, index=True, required=True)

    # is_staff > Designates whether the user can log into special levels of this app
    is_staff = columns.Boolean(default=False)

    # --------------
    # Helpers password
    # --------------
    @staticmethod
    def hash_password(password=None):
        """
        Returns hash from plain password
        """
        if password is not None:
            return pwd_context.encrypt(password)

    def verify_password(self, password):
        """
        Returns True is password is valid, False otherwise
        """
        return pwd_context.verify(password, self.password)

    # --------------
    # Helpers email
    # --------------
    @staticmethod
    def normalize_email(email):
        """
        Normalize the address by lower casing the domain part of the email
        address.
        """
        email = email or ''
        try:
            email_name, domain_part = email.strip().rsplit('@', 1)
        except ValueError:
            pass
        else:
            email = '@'.join([email_name, domain_part.lower()])
        return email


