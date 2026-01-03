import argparse, webbrowser
from .scanner import RepositoryScanner
from .exporters import export_all
from linuxcmdscan.exporters import (export_json,export_csv,export_txt,export_html)


def main():
    p=argparse.ArgumentParser(prog="linuxcmdscan")
    p.add_argument("path",nargs="?",default=".")
    p.add_argument("--ui",action="store_true")
    p.add_argument("--json", action="store_true", help="Export JSON report only")
    p.add_argument("--csv", action="store_true", help="Export CSV report only")
    p.add_argument("--html", action="store_true", help="Export HTML report only")

    args=p.parse_args()

    if args.ui:
        from linuxcmdscan.ui.app_window import launch_ui
        launch_ui(); return

    res = RepositoryScanner().scan(args.path)

    # No flags → export everything
    if not (args.json or args.csv or args.html):
        export_all(res)
        webbrowser.open("reports/linuxcmdscan_report.html")
        return

    # Selective exports
    if args.json:
        export_json(res, "reports")

    if args.csv:
        export_csv(res, "reports")

    if args.html:
        export_html(res, "reports")
        webbrowser.open("reports/linuxcmdscan_report.html")
