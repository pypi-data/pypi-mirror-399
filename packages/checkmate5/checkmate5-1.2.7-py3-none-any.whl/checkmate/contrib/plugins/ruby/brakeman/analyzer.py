# -*- coding: utf-8 -*-


from checkmate.lib.analysis.base import BaseAnalyzer
from checkmate.helpers.docker_runner import get_image, run_json_tool

import logging
import os

logger = logging.getLogger(__name__)


class BrakemanAnalyzer(BaseAnalyzer):

    def summarize(self, items):
        pass

    def analyze(self, file_revision):
        issues = []
        code_dir = os.environ.get("CODE_DIR", os.getcwd())
        image = get_image("CHECKMATE_IMAGE_BRAKEMAN", "presidentbeef/brakeman:latest")

        try:
            json_result = run_json_tool(image, ["brakeman", "-q", "-f", "json", "/workspace"], mount_path=code_dir)
        except Exception:
            json_result = {}

        for issue in json_result.get('warnings', []):
            location = (((issue.get('line'), None),
                         (issue.get('line'), None)),)

            if file_revision.path.endswith(".rb") and file_revision.path in issue.get('file', ''):
                issues.append({
                    'code': issue.get('check_name'),
                    'warning_type': issue.get('warning_type'),
                    'location': location,
                    'data': issue.get('message'),
                    'file': file_revision.path,
                    'line': issue.get('line'),
                    'fingerprint': self.get_fingerprint_from_code(file_revision, location, extra_data=issue.get('message'))
                })

        return {'issues': issues}
