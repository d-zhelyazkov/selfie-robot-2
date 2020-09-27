# coding: utf-8

"""
    Camera API

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: 1.0.0-oas3
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class BaseSettingInfo(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'setting': 'Setting',
        'editable': 'bool'
    }

    attribute_map = {
        'setting': 'setting',
        'editable': 'editable'
    }

    def __init__(self, setting=None, editable=None):  # noqa: E501
        """BaseSettingInfo - a model defined in Swagger"""  # noqa: E501
        self._setting = None
        self._editable = None
        self.discriminator = None
        self.setting = setting
        self.editable = editable

    @property
    def setting(self):
        """Gets the setting of this BaseSettingInfo.  # noqa: E501


        :return: The setting of this BaseSettingInfo.  # noqa: E501
        :rtype: Setting
        """
        return self._setting

    @setting.setter
    def setting(self, setting):
        """Sets the setting of this BaseSettingInfo.


        :param setting: The setting of this BaseSettingInfo.  # noqa: E501
        :type: Setting
        """
        if setting is None:
            raise ValueError("Invalid value for `setting`, must not be `None`")  # noqa: E501

        self._setting = setting

    @property
    def editable(self):
        """Gets the editable of this BaseSettingInfo.  # noqa: E501

        Specifies whether the value of the setting can be edited.  # noqa: E501

        :return: The editable of this BaseSettingInfo.  # noqa: E501
        :rtype: bool
        """
        return self._editable

    @editable.setter
    def editable(self, editable):
        """Sets the editable of this BaseSettingInfo.

        Specifies whether the value of the setting can be edited.  # noqa: E501

        :param editable: The editable of this BaseSettingInfo.  # noqa: E501
        :type: bool
        """
        if editable is None:
            raise ValueError("Invalid value for `editable`, must not be `None`")  # noqa: E501

        self._editable = editable

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        if issubclass(BaseSettingInfo, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, BaseSettingInfo):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
