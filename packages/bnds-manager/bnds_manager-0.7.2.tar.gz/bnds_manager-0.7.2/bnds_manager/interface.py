# Last modified:
from .model import BayesianNetwork
from . import widgets
from . import fields
from .widgets import (
    BaseInputWidget,
    BarChartWidget,
    SliderInputWidget,
    MultipleInputWidget,
    SubInputWidget,
)
from .fields import TextField
import re
import json
import warnings


class InterfaceConfig:
    """
    InterfaceConfig

    def __init__(self, id, name, modelId=None, model=None, description=None, color='#4287f5', display_mode='test',
    input_groups=None, output_groups=None, input_widgets=[], output_widgets=[],
    input_variables=[], output_variables=[], printing_enabled=False):

    Constructs an interface configuration object for upload to the BNDS server.

    A validation check is run on execution of the to_dict method.

    """

    def __init__(
        self,
        id,
        name,
        description=None,
        color="#4287f5",
        display_mode="test",
        input_groups=None,
        output_groups=None,
        input_widgets=[],
        output_widgets=[],
        input_variables=[],
        output_variables=[],
        printing_enabled=False,
        instructions="Welcome to the interface!\nTo create a prediction, press the button on the right, then select as many or as little inputs as you desire.",
        display_widgets=[],
        subject_id_fields=[],
        data_download_enabled=True,
    ):

        self.id = id
        self._check_id()

        self.name = name
        self.description = description
        self.color = color
        self.display_mode = display_mode
        self.printing_enabled = printing_enabled
        self.instructions = instructions
        self.data_download_enabled = data_download_enabled

        self.input_groups = input_groups
        self.output_groups = output_groups
        self._check_groups()

        # - Check input_widgets
        if len(input_widgets) + len(input_variables) == 0:
            raise ValueError(
                "Please provide a list of either input widgets or input variables"
            )

        self.input_widgets = [widget for widget in input_widgets] + [
            BaseInputWidget.from_variable(variable) for variable in input_variables
        ]

        if len(output_widgets) + len(output_variables) == 0:
            raise ValueError(
                "Please provide a list of either input widgets or input variables"
            )

        self.output_widgets = [widget for widget in output_widgets] + [
            BarChartWidget.from_variable(variable) for variable in output_variables
        ]

        self.display_widgets = []

        try:
            self.display_widgets = [widget for widget in display_widgets]
        except Exception as e:
            print(
                "NON-FATAL {}\nNo display widgets recognised. All your display_widgets should be in one list with the key display_widgets at the top level".format(
                    e
                )
            )

        # Initialize subject_id_fields
        self.subject_id_fields = []

        try:
            self.subject_id_fields = [field for field in subject_id_fields]
        except Exception as e:
            print(
                f"NON-FATAL {e}\nNo subject ID fields recognized. Setting to empty list."
            )

        for widget in self.input_widgets:
            if type(widget) == MultipleInputWidget:
                # We need to get the subwidgets out of the MI widget just so the model/intf parser has widget IDs to use when locating the posteriors
                self.input_widgets.extend(widget.generate_sub_widgets())

        # print("input_widgets: ", self.input_widgets)
        # print("input_variables: ", input_variables)

    def input_widget_ids(self):
        return [widget.id for widget in self.input_widgets]

    def get_input_widget(self, idx):
        """
        Input widget structure:
            {
                "type": <string>, // Corresponds to a predefined input widget type
                "id": <string>,
                "title": <string>,
                "group": <string>, // ID of one of the input groups
                "input_variables": [ // Empty if it's a non-BN widget
                    {
                    "modelId": <string>,
                    "variableId": <string>
                    },
                    ...
                ]
                "description": <string>,
                "help_text": <string>,
                "parameters: { ... }, // Usually empty - see widgets page
            }
        """
        return self.input_widgets[self.input_widget_ids().index(idx)]

    def output_widget_ids(self):
        return [widget.id for widget in self.output_widgets]

    def get_output_widget(self, idx):
        return self.output_widgets[self.output_widget_ids().index(idx)]

    def display_widget_ids(self):
        return [widget.id for widget in self.display_widgets]

    def get_display_widget(self, idx):
        return self.display_widgets[self.display_widget_ids().index(idx)]

    def set_printing_enabled(self, val):
        self.printing_enabled = val

    def get_printing_enabled(self):
        return self.printing_enabled

    def _check_id(self):
        if not re.match(r"^[A-Za-z0-9_]{3,20}$", self.id):
            raise ValueError(
                f"The id {self.id} should be lowercase alphanumeric or underscore between 3 and 20 characters"
            )

    @staticmethod
    def _check_group(group):

        if not isinstance(group, dict):
            raise TypeError(
                "Groups must be supplied in a dictionary of id, name and (optionally) description"
            )

        for key in ["id", "name"]:
            if key not in group.keys():
                raise KeyError(f"The supplied group must contain a '{key}' key")

        if not re.match(r"^[a-z0-9_]{3,20}$", group["id"]):
            raise ValueError(
                f"The group id {group['id']} must consist of between 3 and 20 alphanumeric characters and underscores"
            )

    def _check_groups(self):

        for group_list in [self.input_groups, self.output_groups]:

            if not isinstance(group_list, list):
                raise TypeError(
                    "You must provide a list of both input and output groups"
                )

            for group in group_list:
                self._check_group(group)

    @staticmethod
    def _check_widget_group(widget, group_ids):

        if widget.group not in group_ids and type(widget) != SubInputWidget:
            warnings.warn(
                f"The group '{widget.group}' for {widget} is not an id of any the listed groups"
            )
            # Testing out using a warning here so that we can use None groups for MIInputs while still alerting users if there's an issue with their intf

    def _check_widget_groups(self):

        for group_type in ["input", "output"]:

            group_ids = [group["id"] for group in getattr(self, f"{group_type}_groups")]

            for widget in getattr(self, f"{group_type}_widgets"):
                self._check_widget_group(widget, group_ids)

    # def _check_model_ids(self):
    #     """
    #     Goes through every input widget and checks for model IDs. Also checks that the output widgets are the same ones
    #     """
    #     pass

    def _check_unique_ids(self):

        widgets_ids = (
            [widget.id for widget in self.input_widgets]
            + [widget.id for widget in self.output_widgets]
            + [widget.id for widget in self.display_widgets]
        )

        for idx in widgets_ids:
            if sum(idy == idx for idy in widgets_ids) > 1:
                raise ValueError(
                    f"The widget id {idx} is repeated multiple times. All ids must be unique"
                )

    def _check_printing(self):
        if self.printing_enabled != True and self.printing_enabled != False:
            raise ValueError('The flag "printing_enabled" must be True or False.')

    def check(self):
        """
        Overall validation for InterfaceConfig instance
        """

        for widget in self.input_widgets + self.output_widgets:
            widget.check()

        self._check_id()
        self._check_unique_ids()
        self._check_groups()
        self._check_widget_groups()
        self._check_printing()

    def to_dict(self, sort_data=True, sort_key="id"):

        self.check()

        data = {}

        for key in [
            "id",
            "name",
            "description",
            "color",
            "display_mode",
            "printing_enabled",
            "instructions",
            "input_groups",
            "output_groups",
            "data_download_enabled",
        ]:
            if hasattr(self, key):
                data[key] = getattr(self, key)

        data["input_widgets"] = [widget.to_dict() for widget in self.input_widgets]
        data["output_widgets"] = [widget.to_dict() for widget in self.output_widgets]
        data["display_widgets"] = [widget.to_dict() for widget in self.display_widgets]
        data["subject_id_fields"] = [
            field.to_dict() for field in self.subject_id_fields
        ]

        if sort_data:
            data["input_widgets"].sort(key=lambda x: x[sort_key])
            data["output_widgets"].sort(key=lambda x: x[sort_key])
            data["display_widgets"].sort(key=lambda x: x[sort_key])

        return data

    def to_json(self, filename, **kwargs):
        json_string = json.dumps(self.to_dict(**kwargs), indent=2)
        with open(filename, "w") as file:
            file.write(json_string)

    @classmethod
    def from_zest_model(cls, interfaceId, model, **kwargs):
        """
        Constructs an interface from a BayesianNetwork model. The variables of the model must have a group attribute in order to be included as a widget and the model must contain a list of input and output groups.

        Additional kwargs are passed to the InterfaceConfig __init__ method.

        interfaceId: String
        model: BayesianNetwork
        """

        for key in kwargs.keys():
            if key in ["input_groups", "output_groups"]:
                raise KeyError(
                    "input and output groups must be specified for the model rather than passed as arguments"
                )

            if key in ["input_variables", "output_variables"]:
                raise KeyError(
                    "input and output variables are taken dirently from the model rather than specified directly"
                )

        input_groups = model.input_groups
        output_groups = model.output_groups

        input_group_ids = list(map(lambda x: x["id"], input_groups))
        input_variables = list(
            filter(lambda x: x.group in input_group_ids, model.variables)
        )

        output_group_ids = list(map(lambda x: x["id"], output_groups))
        output_variables = list(
            filter(lambda x: x.group in output_group_ids, model.variables)
        )

        printing_enabled = 0
        data_download_enabled = True
        instructions = "Welcome to the interface!\nTo create a prediction, press the button on the right, then select as many or as little inputs as you desire."
        try:
            printing_enabled = model.printing_enabled
        except:
            pass
        try:
            instructions = model.instructions
        except:
            pass

        name = model.name

        if "name" in kwargs:
            name = kwargs["name"]
            del kwargs["name"]

        return cls(
            interfaceId,
            name,
            # modelId=model.id,
            input_groups=input_groups,
            output_groups=output_groups,
            input_variables=input_variables,
            output_variables=output_variables,
            printing_enabled=printing_enabled,
            instructions=instructions,
            data_download_enabled=data_download_enabled,
            **kwargs,
        )

    @classmethod  # TODO: Needs MMI changes - just add loop to format the widgets properly since we know their id
    def from_saved_model(cls, interfaceId, filename, **kwargs):
        """
        Constructs an interface from a saved bn_zest BayesianNetwork json file. The variables of the model must have a group attribute in order to be included as a widget and the model must contain a list of input and output groups.

        Additional kwargs are passed to the InterfaceConfig __init__ method.

        interfaceId: String
        filename: String
        """

        model = BayesianNetwork.from_json(filename)
        return cls.from_zest_model(interfaceId, model, **kwargs)

    @classmethod
    def from_dict(cls, data):
        def process_widget(data):
            # This function turns the widget dicts into widget objects
            # print("process_widget",data)
            widget_type = f"{data['type']}Widget"
            del data["type"]
            return getattr(widgets, widget_type)(**data)

        def process_field(data):
            # This function turns the subject identification field dicts into field objects
            # print("process_field",data)
            field_type = f"{data['type'].title()}Field"
            del data["type"]
            return getattr(fields, field_type)(**data)

        if "modelId" in data:
            # THIS IS CURRENTLY THE ONLY CHECK THAT WE USE TO SEE IF THE INTERFACE IS CORRECTLY FORMED FOR MMI
            # it will be reinforced with better checking in the future!
            for i in range(len(data["input_widgets"])):
                if "input_variables" not in data["input_widgets"][i]:
                    if (data["input_widgets"][i]["type"] != "DropDownNonBNInput") and (
                        data["input_widgets"][i]["type"] != "FreeTextNonBNInput"
                    ):
                        print(data["input_widgets"][i]["type"])
                        data["input_widgets"][i]["input_variables"] = [
                            {
                                "modelId": data["modelId"],
                                "variableId": data["input_widgets"][i]["variableId"],
                            }
                        ]
                        data["input_widgets"][i].pop("variableId")
            for j in range(len(data["output_widgets"])):
                if (
                    len(data["output_widgets"][j]["output_variables"]) != 2
                ):  # Each entry of output_variables should be 2 pieces of data [{modelid1, variableid1}...]
                    output_vars = []
                    for variable in data["output_widgets"][j]["output_variables"]:
                        output_vars.append(
                            {"modelId": data["modelId"], "variableId": variable}
                        )
                    data["output_widgets"][j]["output_variables"] = output_vars

            data.pop("modelId")
        if (
            "interface_models" in data
        ):  # This tag is added during download but is not useful when reuploading, so we prune it
            data.pop("interface_models")

        # print("DATA INPUT_WIDGETS",data['input_widgets'])
        data["input_widgets"] = [
            process_widget(widget) for widget in data["input_widgets"]
        ]
        data["output_widgets"] = [
            process_widget(widget) for widget in data["output_widgets"]
        ]
        try:
            data["subject_id_fields"] = [
                process_field(field) for field in data["subject_id_fields"]
            ]
        except KeyError:
            # Add default subject_id_field if not found
            data["subject_id_fields"] = [
                TextField(title="Subject ID", description="Enter subject identifier")
            ]
        try:
            data["display_widgets"] = [
                process_widget(widget) for widget in data["display_widgets"]
            ]
        except KeyError:
            data["display_widgets"] = []
        # print("POST-DATA", data)
        return cls(**data)

    @classmethod
    def from_json(cls, filename):
        with open(filename, "r") as file:
            file_string = file.read()

        print(json.loads(file_string))
        return cls.from_dict(json.loads(file_string))

    def __getitem__(self, item):
        return self.get_output_widget(item)

    def __setitem__(self, item, value):
        idx = self.output_widget_ids().index(item)
        self.output_widgets[idx] = value

    def __repr__(self):
        return f"Interface({self.id})"
