# -*- coding: utf-8 -*-


from checkmate.lib.analysis.base import BaseAnalyzer
from checkmate.helpers.docker_runner import get_image, run_json_tool
import logging
import os
import json

logger = logging.getLogger(__name__)


class SemgrepjavaAnalyzer(BaseAnalyzer):

    def __init__(self, *args, **kwargs):
        super(SemgrepjavaAnalyzer, self).__init__(*args, **kwargs)
        try:
            result = subprocess.check_output(
                ["semgrep", "--version"],stderr=subprocess.DEVNULL).strip()
        except subprocess.CalledProcessError:
            logger.error(
                "Cannot initialize semgrep analyzer: Executable is missing, please install it.")
            raise

    def summarize(self, items):
        pass

    def analyze(self, file_revision):
        issues = []
        code_dir = os.environ.get("CODE_DIR", os.getcwd())
        image = get_image("CHECKMATE_IMAGE_SEMGREP", "returntocorp/semgrep:latest")
        target = os.path.join("/workspace", file_revision.path.lstrip("/"))

        try:
            result = run_json_tool(
                image,
                ["semgrep", "--config", "p/find-sec-bugs", "--no-git-ignore", "--json", target],
                mount_path=code_dir,
            )
        except Exception:
            result = {}

        for issue in result.get('results', []):

            location = (((issue.get('start', {}).get('line'), None),
                         (issue.get('start', {}).get('line'), None)),)

            if file_revision.path.endswith((".java", ".jsp", ".scala")):
                val = issue.get('check_id', '')
                val = val.replace("root.", "")
                val = val.title().replace("_", "")

                issues.append({
                    'code': val,
                    'location': location,
                    'data': issue.get('extra', {}).get('message'),
                    'file': file_revision.path,
                    'line': issue.get('start', {}).get('line'),
                    'fingerprint': self.get_fingerprint_from_code(file_revision, location, extra_data=issue.get('extra', {}).get('message'))
                })

        return {'issues': issues}
