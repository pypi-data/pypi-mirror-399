class FilterField:
    def __init__(self, field_name=None):
        self.field_name = field_name
        self.operator = None
        self.value = None
        self.conjunction = None
        self.conditions = []
        self.children = []

    def __eq__(self, value):
        return self._create_condition("is", value)

    def __ne__(self, value):
        return self._create_condition("isNot", value)

    def __ge__(self, value):
        return self._create_condition("isGreaterEqual", value)

    def __gt__(self, value):
        return self._create_condition("isGreater", value)

    def __le__(self, value):
        return self._create_condition("isLessEqual", value)

    def __lt__(self, value):
        return self._create_condition("isLess", value)

    def contains(self, value):
        return self._create_condition("contains", value)

    def notContains(self, value):
        return self._create_condition("doesNotContain", value)

    def isEmpty(self):
        return self._create_condition("isEmpty", [])

    def isNotEmpty(self):
        return self._create_condition("isNotEmpty", [])

    def _create_condition(self, operator, value):
        condition = FilterField(self.field_name)
        condition.operator = operator
        if isinstance(value, list):
            condition.value = [str(v) for v in value]
        else:
            condition.value = [str(value)]
        return condition

    def __and__(self, other):
        combined = FilterField("")
        combined.conjunction = "and"

        if (not self.conditions and not self.children) and (not other.conditions and not other.children):
            combined.conditions = [
                {"field_name": self.field_name,
                    "operator": self.operator, "value": self.value},
                {"field_name": other.field_name,
                    "operator": other.operator, "value": other.value}
            ]
        else:
            combined.children = [self, other]

        return combined

    def __or__(self, other):
        combined = FilterField("")
        combined.conjunction = "or"

        if (not self.conditions and not self.children) and (not other.conditions and not other.children):
            combined.conditions = [
                {"field_name": self.field_name,
                    "operator": self.operator, "value": self.value},
                {"field_name": other.field_name,
                    "operator": other.operator, "value": other.value}
            ]
        else:
            combined.children = [self, other]

        return combined

    def to_dict(self):
        result = {"filter": {}}
        filter_dict = result["filter"]

        filter_dict["conjunction"] = self.conjunction or "and"

        if self.conditions:
            filter_dict["conditions"] = self.conditions

        if self.children:
            children_list = []
            for child in self.children:
                if hasattr(child, 'to_dict'):
                    child_dict = child.to_dict()
                    if "filter" in child_dict:
                        children_list.append(child_dict["filter"])
                    else:
                        children_list.append(child_dict)
                else:
                    children_list.append(child)
            filter_dict["children"] = children_list

        if (self.operator is not None and
            not self.conditions and
            not self.children and
                self.field_name is not None):
            filter_dict["conditions"] = [
                {
                    "field_name": self.field_name,
                    "operator": self.operator,
                    "value": self.value
                }
            ]

        return result
