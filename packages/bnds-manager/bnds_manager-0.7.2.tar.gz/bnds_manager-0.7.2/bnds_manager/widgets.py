# Last modified: 2025/03/06 15:42:10
import re


class BaseWidget:
    """
    Base Widget.
    """

    parameters = {}

    def __init__(
        self, id, title, group, description=None, help_text=None, parameters=None, order=None
    ):

        self.id = id
        self.title = title
        self.group = group
        self.description = description
        self.help_text = help_text
        self.parameters = self.parameters.copy()
        self.order = order

        if isinstance(parameters, dict):
            self.parameters.update(parameters)

        self.check()

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, value):
        if not re.match(r"^[a-z0-9_]{1,20}$", value):
            raise ValueError(
                f"The id {value} should only consist of letters, numbers or underscore and be no more than 20 characters"
            )

        self.__id = value

    def check(self):
        pass

    def to_dict(self):

        self.check()

        data = {"type": self.__class__.__name__.split("Widget")[0]}

        for key in self.__init__.__code__.co_varnames:
            if hasattr(self, key):
                data[key] = getattr(self, key)

        return data

    def __repr__(self):
        return f"{self.__class__.__name__}({self.id})"


# - Input widgets


class BaseInputWidget(BaseWidget):

    def __init__(
        self,
        id,
        title,
        group,
        input_variables,
        order=None,
        description=None,
        help_text=None,
        parameters=None,
    ):
        super().__init__(
            id,
            title,
            group,
            description=description,
            help_text=help_text,
            parameters=parameters,
            order=order,
        )
        self.input_variables = input_variables

    @property
    def input_variables(self):
        return self.__input_variables

    @input_variables.setter
    def input_variables(self, value):

        if not isinstance(value, list):
            raise TypeError("input_variables must be a list")

        for pair in value:
            if not isinstance(pair, dict):
                raise TypeError("the values in input_variables must be dicts")
            
        
        
        self.__input_variables = value


class MultipleInputWidget(BaseInputWidget):
    
    """
    This is the only input widget that has more than one variable
    Example format:
    {
      "type": "MultipleInput",
      "id": "ll_variables",
      "title": "Lower limb amputation",
      "group": "injury",
      "input_variables": [
    [
        {
            "modelId": "transfusion",
            "variableId": "jjj_ll_amp"
        },
        {
            "modelId": "survivalrevised",
            "variableId": "kkk_amputation_ll"
        }
    ],
    [
        {
            "modelId": "transfusion",
            "variableId": "hhh_ll_frac"
        },
        {
            "modelId": "survivalrevised",
            "variableId": "iii_b_lb_fracture_ll"
        }
    ]],
        }
    """
    parameters = {
    }
    
    
    
    def __init__(self, id, title, group, input_variables, description=None, help_text=None, parameters=None, order=None):
        super().__init__(id, title, group, input_variables, description=description, help_text=help_text, parameters=parameters, order=order)
        
        
    @property
    def input_variables(self):
        return self.__input_variables

    @input_variables.setter
    def input_variables(self, value):

        if not isinstance(value, list):
            raise TypeError("input_variables on MultipleInputWidget must be a list")
        
        for item in value:
            if not isinstance(item, list):
                raise TypeError("input_variables on MultipleInputWidget must be a list of lists")

        for item in value:
            for pair in item:
                if not isinstance(pair, dict):
                    raise TypeError("the values in input_variables must be dicts")
            
        
        
        self.__input_variables = value

    def generate_sub_widgets(self):
        """
        parameters = {
            alt_states = [["Yes", "No"], ["High blood pressure", "Low blood pressure"], [0, 1],[3, 2]],
        }
        """
        sub_widgets = []
        for i in range(len(self.input_variables)):
            sub_title = self.title
            if(len(self.id) <= 20 - len(str(i))): # widget ID is varchar(20) in interface_inputs
                sub_id = self.id + str(i) # Edge case where this all fails is if two MI widgets are 20 characters long and only differ on the last character - users don't typically use numbers in widget ids
            else:
                sub_id = self.id[0:len(self.id) - len(str(i))] + str(i)
            try:
                sub_title = self.parameters["title"][i] # title must be formatted for MI widgets as an array
            except:
                print("NON-FATAL ERROR: each subwidget of MultipleInputWidget must have a title listed in the parameters under parameters = {title = [title1, ..., titlen]}")
            sub_group = None
            sub_parameters = {}
            for key in set(self.parameters) - set(["sub_widgets"]):
                sub_parameters[key] = self.parameters[key][i]
            
            sub_widgets.append(SubInputWidget(sub_id, sub_title, sub_group, self.input_variables[i], description=None, help_text=None, parameters=sub_parameters)) # TODO: Need to figure out parameters
        self.input_variables = [] #TODO: this fixes the DB upload of this widget
        self.parameters["sub_widgets"] = [  w.to_dict() for w in sub_widgets ]
        return sub_widgets



class SubInputWidget(BaseInputWidget):
    
    """
    This is a BaseInputWidget but only for use inside other widgets. It should NOT be instantiated by itself.
    A MultipleInputWidget object generates one SubInputWidget for each distinct variable in its input_variables list
    """
    
    def __init__(
        self,
        id,
        title,
        group,
        input_variables,
        description=None,
        help_text=None,
        parameters=None,
        order=None
    ):
        super().__init__(
            id,
            title,
            group,
            input_variables,
            description=description,
            help_text=help_text,
            parameters=parameters,
            order=order
        )
        self.input_variables = input_variables

    @property
    def input_variables(self):
        return self.__input_variables

    @input_variables.setter
    def input_variables(self, value):

        if not isinstance(value, list):
            raise TypeError("input_variables must be a list")

        for pair in value:
            if not isinstance(pair, dict):
                raise TypeError("the values in input_variables must be dicts")
            
        
        
        self.__input_variables = value



class SliderInputWidget(BaseInputWidget):
    """
    This widget is used for inputting continuous variables via a slider and text input box
    min: the lowest value the input can take (inclusive)
    max: the highest value the input can take (inclusive)
    step: the difference between each possible input
    """

    parameters = {
        "min": 0,
        "max": 100,
        "step": 1,
        "unit": "",
    }

    def __init__(
        self,
        id,
        title,
        group,
        input_variables,
        description=None,
        help_text=None,
        parameters=None,
        order=None
    ):
        super().__init__(
            id,
            title,
            group,
            input_variables,
            description=description,
            help_text=help_text,
            parameters=parameters,
            order=order
        )
        
    def check(self):
        if self.parameters["min"] >= self.parameters["max"]:
            raise ValueError(f"The value of min must be lower than max for {self}")

        if self.parameters["step"] > abs(
            self.parameters["max"] - self.parameters["min"]
        ):
            raise ValueError(
                f"The value of step must be smaller than the difference between the min and max values for {self}"
            )

        if "min" not in self.parameters.keys():
            raise KeyError(f"Please provide a min parameter for {self}")

        if "max" not in self.parameters.keys():
            raise KeyError(f"Please provide a max parameter for {self}")

        if "step" not in self.parameters.keys():
            raise KeyError(f"Please provide a step parameter for {self}")

        if "unit" not in self.parameters.keys():
            raise KeyError(f"Please provide a unit parameter for {self}")


class FreeTextNonBNInputWidget(BaseWidget):
    """
    This widget is used to provide a limited free text section for notes on the dashboard
    """

    parameters = {"maxLength": 128, "message": ""}

    def __init__(
        self,
        id,
        title,
        group,
        description=None,
        help_text=None,
        parameters=None,
        order=None,
    ):
        super().__init__(
            id,
            title,
            group,
            description=description,
            help_text=help_text,
            parameters=parameters,
            order=order
        )

    def check(self):
        if "maxLength" not in self.parameters.keys():
            raise KeyError(f"Please provide a maxLength parameter for {self}")

        if not (self.parameters["maxLength"] > 0) or not isinstance(
            self.parameters["maxLength"], int
        ):
            raise ValueError(f"The maxLength parameter must be a positive integer.")


# - Output widgets


class BaseOutputWidget(BaseWidget):

    def __init__(
        self,
        id,
        title,
        group,
        output_variables,
        description=None,
        help_text=None,
        parameters=None,
        order=None,
    ):
        super().__init__(
            id,
            title,
            group,
            description=description,
            help_text=help_text,
            parameters=parameters,
            order=order,
        )
        self.output_variables = output_variables

    @property
    def output_variables(self):
        return self.__output_variables

    @output_variables.setter
    def output_variables(self, value):

        value = [value] if isinstance(value, str) else value

        if not isinstance(value, list):
            raise TypeError("output_variables must be a list")

        self.__output_variables = value

    @classmethod
    def from_variable(cls, variable, **kwargs):
        description = (
            None if not hasattr(variable, "description") else variable.description
        )
        return cls(
            variable.id,
            variable.name,
            variable.group,
            [variable.id],
            description=description,
            **kwargs,
        )


class CustomOutputWidget(BaseOutputWidget):
    """
    Useful in situation where a specific widget is not recognized.
    Specify a type to overcome lack of recognition
    """

    def __init__(
        self,
        id,
        title,
        group,
        output_variables,
        type_="BarChart",
        order=None,
        description=None,
        help_text=None,
        parameters=None,
    ):
        super().__init__(
            id,
            title,
            group,
            output_variables,
            order=order,
            description=description,
            help_text=help_text,
            parameters=parameters,
        )
        self.type_ = type_

    def to_dict(self):
        data = super().to_dict()
        data["type"] = self.type_
        return data


class BarChartWidget(BaseOutputWidget):
    pass


class PieChartWidget(BaseOutputWidget):
    pass


class IconArrayWidget(BaseOutputWidget):
    pass


class StateChangeWidget(BaseOutputWidget):
    pass


class BarChartIndicatorWidget(BaseOutputWidget):
    pass


class RiskStratificationWidget(BaseOutputWidget):

    parameters = {
        "target_states": [1],
        "strata": [20, 20, 20, 20, 20],
        "strataColor": [
            "rgba(52, 162, 40, 1)",
            "rgba(172, 198, 58, 1)",
            "rgba(228, 208, 32, 1)",
            "rgba(230, 130, 53, 1)",
            "rgba(203, 55, 52, 1)",
        ],
        "strataNames": [
            "Very low risk",
            "Low risk",
            "Medium risk",
            "High risk",
            "Very high risk",
        ],
        "truncatedMax": 100,
        "enableKey": False
    }

    def check(self):

        if sum(self.parameters["strata"]) != 100:
            raise ValueError(f"The sum of strata for {self} must equal 100")

        if "target_states" not in self.parameters.keys():
            raise KeyError(f"Please provide a target_states parameter for {self}")

        if "strataColor" not in self.parameters.keys():
            raise KeyError(f"Please provide a strataColor parameter for {self}")

        if "strataNames" not in self.parameters.keys():
            raise KeyError(f"Please provide a strataNames parameter for {self}")    

        if len(self.parameters["strata"]) != len(self.parameters["strataColor"]):
            raise ValueError(
                f"The number of strata in {self} must match the number of strataColor"
            )

        if len(self.parameters["strata"]) != len(self.parameters["strataNames"]):
            raise ValueError(
                f"The number of strata in {self} must match the number of strataNames"
            )

        if "riskValues" in self.parameters.keys():

            riskVals = self.parameters["riskValues"]

            if not all(isinstance(l, list) for l in riskVals):
                raise TypeError(
                    f"The riskValues parameter for {self} must be a list of numbered lists"
                )

            for vals in riskVals:
                if len(vals) != len(self.parameters["strata"]):
                    raise ValueError(
                        f"The number of values in each set of riskValues for {self} must equal the number of strata"
                    )
        
        if "enableKey" not in self.parameters.keys():
            raise KeyError(f"Please provide a target_states parameter for {self}")
        
        if not isinstance(self.parameters["enableKey"], bool):
            raise TypeError(
                f"The enableKey parameter for {self} must be True or False"
            )
            


class DynamicChartWidget(RiskStratificationWidget):
    pass
        

class AggregateBarChartWidget(BaseOutputWidget):
    
    parameters = {
        "max": 30,
        "unit": "units",
        "average_values" : {"variable": ["data"]}
    }
    
    #     self.output_variables = output_variables
    
    # def check(self):
    #     average_values = self.parameters["average_values"]
    #     for key in average_values:
    #         if key not in self.output_variables:
    #             raise KeyError("The variables listed in average_values must be the same as the values in output_variables")
    #         # if len(average_values[key]) != len(): # Need to say that the length = length of states from that same variable in the model
    

# Display Widgets
# Currently there's only one type of DisplayWidget, and it defines what shows up on the left hand side of the output view

class DisplayWidget(BaseWidget):
    
    parameters = {
        "icon": "View",
        "input_items": [
                ],
        "formatted_strings": [
                ],
        "display_empty": False,
        "show_title_column": True
    }
    
    def __init__(
        self,
        id,
        title,
        order=None,
        description=None,
        help_text=None,
        parameters=None,
    ):
        super().__init__(
            id,
            title,
            group=None,
            description=description,
            help_text=help_text,
            parameters=parameters,
            order=order,
        )
        
    def check(self):
        pass