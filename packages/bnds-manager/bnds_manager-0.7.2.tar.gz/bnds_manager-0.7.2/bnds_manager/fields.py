class BaseField:
    """
    Base Subject Identification Field.
    
    This is the abstract base class for all field types used in subject identification.
    It provides common functionality for field validation, serialization, and basic
    attributes that all fields share.
    
    Attributes:
        title (str): The display title for the field
        description (str, optional): A longer description of the field's purpose
        help_text (str, optional): Help text to guide users when filling out the field
        mandatory (bool): Whether this field is required (default: False)
        modifiable (bool): Whether this field can be modified after creation (default: True)
        filterable (bool): Whether this field can be used for filtering. Only CategoryField can be filtered. (default: True)
        parameters (dict): Additional parameters specific to the field type
        order (int): Order which the field appears in interface
    """

    parameters = {}

    def __init__(
        self,
        title,
        description=None,
        help_text=None,
        mandatory=False,
        modifiable=True,
        filterable=False,
        parameters=None,
        order=99,
    ):

        self.title = title
        self.description = description
        self.help_text = help_text
        self.mandatory = mandatory
        self.modifiable = modifiable
        self.filterable = filterable
        self.parameters = self.parameters.copy()
        self.order = order

        if isinstance(parameters, dict):
            self.parameters.update(parameters)

    def to_dict(self):
        """
        Convert the field to a dictionary representation.
        
        This method calls check() to validate the field before serialization,
        then creates a dictionary containing the field type and all its attributes.
        
        Returns:
            dict: A dictionary representation of the field suitable for JSON serialization
            
        Raises:
            Various exceptions from check() method if validation fails
        """

        self.check()

        # Field types are lower case letters in bnds_server like category, text, date, datetime
        data = {"type": self.__class__.__name__.split("Field")[0].lower()}

        for key in self.__init__.__code__.co_varnames:
            if hasattr(self, key):
                data[key] = getattr(self, key)

        return data

    def __repr__(self):
        return f"{self.__class__.__name__}({self.title})"

    def check(self):
        """
        Validate the field configuration.
        
        This is a base implementation that performs no validation.
        Subclasses should override this method to implement field-specific validation.
        
        Raises:
            Various exceptions if validation fails (implementation depends on subclass)
        """
        pass


class CategoryField(BaseField):
    def check(self):
        # Check if states parameter exists
        if 'states' not in self.parameters:
            raise ValueError(f"CategoryField '{self.title}' must have 'states' in parameters")
        
        # Check if states is a list
        if not isinstance(self.parameters['states'], list):
            raise TypeError(f"CategoryField '{self.title}' parameter 'states' must be a list")
        
        # Check if all items in states are strings
        if not all(isinstance(state, str) for state in self.parameters['states']):
            raise TypeError(f"CategoryField '{self.title}' parameter 'states' must be a list of strings")
        
        # Check if states list is not empty
        if len(self.parameters['states']) == 0:
            raise ValueError(f"CategoryField '{self.title}' parameter 'states' cannot be empty")


class DateField(BaseField):
    """
    A field for date input.
    
    This field type is used when users need to enter a date value (without time).
    The field inherits all functionality from BaseField without additional validation
    or parameters.
    
    Example:
        field = DateField(
            title="Date of Birth",
            description="Enter your date of birth",
            mandatory=True,
            parameters = {
                "min": "2025-01-01",
                "max": "2027-12-31"
            }
        )
    """
    pass


class DatetimeField(BaseField):
    """
    A field for datetime input.
    
    This field type is used when users need to enter both date and time values.
    The field inherits all functionality from BaseField without additional validation
    or parameters.
    
    Example:
        field = DatetimeField(
            title="Appointment Time",
            description="Select your appointment date and time",
            mandatory=True,
            parameters = {
                "min": "2025-01-01T00:00",
                "max": "2027-12-31T23:59"
            }
        )
    """
    pass


class TextField(BaseField):
    """
    A field for free-form text input.
    
    This field type is used when users need to enter arbitrary text data.
    The field inherits all functionality from BaseField without additional validation
    or parameters.
    
    Example:
        field = TextField(
            title="Subject ID",
            description="Enter the unique subject identifier",
            mandatory=True,
            help_text="Format: SUB-XXXX where X is a number",
            parameters = {
                "rows" = 2
            }

        )
    """
    pass
