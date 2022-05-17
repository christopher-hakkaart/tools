#!/usr/bin/env python

import os

import yaml


def multiqc_config(self):
    """Make sure basic multiQC plugins are installed and plots are exported
    Basic template:

    .. code-block:: yaml
        report_comment: >
            This report has been generated by the <a href="https://github.com/nf-core/quantms" target="_blank">nf-core/quantms</a>
            analysis pipeline. For information about how to interpret these results, please see the
            <a href="https://nf-co.re/quantms" target="_blank">documentation</a>.
        report_section_order:
            software_versions:
                order: -1000
            nf-core-quantms-summary:
                order: -1001

        export_plots: true
    """
    passed = []
    warned = []
    failed = []

    fn = os.path.join(self.wf_path, "assets", "multiqc_config.yml")

    # Return a failed status if we can't find the file
    if not os.path.isfile(fn):
        return {"ignored": ["'assets/multiqc_config.yml' not found"]}

    try:
        with open(fn, "r") as fh:
            mqc_yml = yaml.safe_load(fh)
    except Exception as e:
        return {"failed": ["Could not parse yaml file: {}, {}".format(fn, e)]}

    # Check that the report_comment exists and matches
    try:
        assert "report_section_order" in mqc_yml
        orders = dict()
        summary_plugin_name = f"nf-core-{self.pipeline_name}-summary"
        min_plugins = ["software_versions", summary_plugin_name]
        for plugin in min_plugins:
            assert plugin in mqc_yml["report_section_order"], f"Section {plugin} missing in report_section_order"
            assert "order" in mqc_yml["report_section_order"][plugin], f"Section {plugin} 'order' missing. Must be < 0"
            plugin_order = mqc_yml["report_section_order"][plugin]["order"]
            assert plugin_order < 0, f"Section {plugin} 'order' must be < 0"

        for plugin in mqc_yml["report_section_order"]:
            if "order" in mqc_yml["report_section_order"][plugin]:
                orders[plugin] = mqc_yml["report_section_order"][plugin]["order"]

        assert orders[summary_plugin_name] == min(
            orders.values()
        ), f"Section {summary_plugin_name} should have the lowest order"
        orders.pop(summary_plugin_name)
        assert orders["software_versions"] == min(
            orders.values()
        ), f"Section software_versions should have the second lowest order"
    except (AssertionError, KeyError, TypeError) as e:
        failed.append(f"'assets/multiqc_config.yml' does not meet requirements: {e}")
    else:
        passed.append("'assets/multiqc_config.yml' follows the ordering scheme of the minimally required plugins.")

    # Check that the minimum plugins exist and are coming first in the summary
    try:
        assert "report_comment" in mqc_yml
        assert (
            mqc_yml["report_comment"].strip()
            == f'This report has been generated by the <a href="https://github.com/nf-core/{self.pipeline_name}" target="_blank">nf-core/{self.pipeline_name}</a> analysis pipeline. For information about how to interpret these results, please see the <a href="https://nf-co.re/{self.pipeline_name}" target="_blank">documentation</a>.'
        )
    except (AssertionError, KeyError, TypeError):
        failed.append("'assets/multiqc_config.yml' does not contain a matching 'report_comment'.")
    else:
        passed.append("'assets/multiqc_config.yml' contains a matching 'report_comment'.")

    # Check that export_plots is activated
    try:
        assert "export_plots" in mqc_yml
        assert mqc_yml["export_plots"] == True
    except (AssertionError, KeyError, TypeError):
        failed.append("'assets/multiqc_config.yml' does not contain 'export_plots: true'.")
    else:
        passed.append("'assets/multiqc_config.yml' contains 'export_plots: true'.")

    return {"passed": passed, "failed": failed}
