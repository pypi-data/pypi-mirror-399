import pytest
from flybook.bitable import FilterField


class TestFilterField:
    def test_comparison_operators(self):
        query = FilterField("销售额") == "10000.00"
        expected = {
            "filter": {
                "conjunction": "and",
                "conditions": [
                    {
                        "field_name": "销售额",
                        "operator": "is",
                        "value": ["10000.00"]
                    }
                ]
            }
        }
        assert query.to_dict() == expected

    def test_logic_operators(self):
        query = (FilterField("销售额") > "20000.00") & (
            FilterField("职位") != "高级销售员")
        expected = {
            "filter": {
                "conjunction": "and",
                "conditions": [
                    {
                        "field_name": "销售额",
                        "operator": "isGreater",
                        "value": ["20000.00"]
                    },
                    {
                        "field_name": "职位",
                        "operator": "isNot",
                        "value": ["高级销售员"]
                    }
                ]
            }
        }
        assert query.to_dict() == expected

    def test_compound_operators(self):
        query = (
            ((FilterField("销售额") <= "20000.00") | (FilterField("职位").notContains("经理"))) &
            FilterField("职位").isNotEmpty()
        )
        expected = {
            "filter": {
                "conjunction": "and",
                "children": [
                    {
                        "conjunction": "or",
                        "conditions": [
                            {
                                "field_name": "销售额",
                                "operator": "isLessEqual",
                                "value": ["20000.00"]
                            },
                            {
                                "field_name": "职位",
                                "operator": "doesNotContain",
                                "value": ["经理"]
                            }
                        ]
                    },
                    {
                        "conjunction": "and",
                        "conditions": [
                            {
                                "field_name": "职位",
                                "operator": "isNotEmpty",
                                "value": []
                            }
                        ]
                    }
                ]
            }
        }
        assert query.to_dict() == expected
