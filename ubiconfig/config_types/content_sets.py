"""This module abstracts the 'content_sets' mappings"""


class ContentSetMapping(object):
    def __init__(self, input_content, output_content):
        self.input = input_content
        self.output = output_content


class Rpm(ContentSetMapping):
    """Input-output rpm content sets mapping"""

    @property
    def type(self):
        return "rpm"


class Srpm(ContentSetMapping):
    """Input-output srpm content sets mapping"""

    @property
    def type(self):
        return "srpm"


class Debuginfo(ContentSetMapping):
    """Input-output debuginfo content sets mapping"""

    @property
    def type(self):
        return "debuginfo"


class ContentSetsMapping(object):
    def __init__(self, rpm, srpm, debuginfo):
        """
        Args:
            rpm(:class:`Rpm`): rpm content sets mapping
            srpm(:class:`Srpm`): srpm content sets mapping
            debuginfo(:class:`Debuginfo`): debuginfo content sets mapping
        """
        self.rpm = rpm
        self.srpm = srpm
        self.debuginfo = debuginfo

    @classmethod
    def load_from_dict(cls, data):
        """Create instances of :class:`ContentSetsMapping` from a dictionary

        Args:
            data(dict): dictionary with data of following format

        .. code-block:: json

            {
                "rpm": {"input": "<input_content_set>",
                        "output":"<output_content_set>"},
                "srpm": {"input": "<input_content_set>",
                         "output":"<output_content_set>"},
                "debuginfo": {"input": "<input_content_set>",
                              "output":"<output_content_set>"}
            }
        """
        rpm_data = data.get("rpm", {})
        rpm = Rpm(rpm_data.get("input", ""), rpm_data.get("output", ""))

        srpm_data = data.get("srpm", {})
        srpm = Srpm(srpm_data.get("input", ""), srpm_data.get("output", ""))

        debug_data = data.get("debuginfo", {})
        debuginfo = Debuginfo(debug_data.get("input", ""), debug_data.get("output", ""))

        return cls(rpm, srpm, debuginfo)

    def export_dict(self):
        """Return a dictionary such as {type: (input, outpt)}"""
        attributes = [self.rpm, self.srpm, self.debuginfo]
        return dict((m.type, (m.input, m.output)) for m in attributes)
