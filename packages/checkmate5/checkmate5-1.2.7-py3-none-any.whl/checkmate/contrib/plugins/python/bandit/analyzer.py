# -*- coding: utf-8 -*-


from checkmate.lib.analysis.base import BaseAnalyzer
from checkmate.helpers.docker_runner import get_image, run_json_tool

import logging
import os

logger = logging.getLogger(__name__)


class BanditAnalyzer(BaseAnalyzer):

    def summarize(self, items):
        pass

    def analyze(self, file_revision):
        issues = []
        code_dir = os.environ.get("CODE_DIR", os.getcwd())
        target = os.path.join("/workspace", file_revision.path.lstrip("/"))

        image = get_image("CHECKMATE_IMAGE_BANDIT", "pycqa/bandit:latest")
        try:
            json_result = run_json_tool(image, ["bandit", "-f", "json", target], mount_path=code_dir)
        except Exception:
            json_result = {}

        for issue in json_result.get('results', []):
            location = (((issue.get('line_number'), None),
                         (issue.get('line_number'), None)),)
            if file_revision.path.endswith(".py"):
                issues.append({
                    'code': issue.get('test_id'),
                    'location': location,
                    'data': issue.get('issue_text'),
                    'file': file_revision.path,
                    'line': issue.get('line_number'),
                    'fingerprint': self.get_fingerprint_from_code(file_revision, location, extra_data=issue.get('issue_text'))
                })

        return {'issues': issues}
