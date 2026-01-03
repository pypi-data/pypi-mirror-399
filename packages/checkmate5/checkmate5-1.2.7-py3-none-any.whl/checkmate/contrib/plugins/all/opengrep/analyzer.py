# -*- coding: utf-8 -*-

from checkmate.lib.analysis.base import BaseAnalyzer
from checkmate.helpers.docker_runner import get_image, run_json_tool

import logging
import os
import json

logger = logging.getLogger(__name__)


class OpengrepAnalyzer(BaseAnalyzer):
    def summarize(self, items):
        pass

    def analyze(self, file_revision):
        issues = []
        code_dir = os.environ.get("CODE_DIR", os.getcwd())
        image = get_image("CHECKMATE_IMAGE_OPENGREP", "betterscan/opengrep:latest")

        target = os.path.join("/workspace", file_revision.path.lstrip("/"))
        try:
            json_result = run_json_tool(image, ["opengrep", "scan", "--no-git-ignore", "--json", target], mount_path=code_dir)
        except Exception:
            json_result = {}

        for issue in json_result.get("results", []):
            location = (
                ((issue.get("start", {}).get("line"), None), (issue.get("start", {}).get("line"), None)),
            )
            val = (issue.get("check_id") or "").replace("root.", "")
            val = val.title().replace("_", "")

            issues.append(
                {
                    "code": val,
                    "location": location,
                    "data": issue.get("extra", {}).get("message"),
                    "file": file_revision.path,
                    "line": issue.get("start", {}).get("line"),
                    "fingerprint": self.get_fingerprint_from_code(
                        file_revision, location, extra_data=issue.get("extra", {}).get("message")
                    ),
                }
            )

        return {"issues": issues}
