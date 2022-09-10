
from .. import checks
from . import Check

class TopLevelCheck(Check):
    type = "manifest"

    def check(self, manifest):
        build_extension = manifest.get("build-extension")

        if not build_extension:
            command = manifest.get("command")
            if not command:
                self.errors.append("toplevel-no-command")
            elif command.startswith("/"):
                self.warnings.append("toplevel-command-is-path")

        branch = manifest.get("branch")

        if branch == "stable" or branch == "master":
            self.errors.append("toplevel-unecessary-branch")

        default_branch = manifest.get("default-branch")
        if default_branch == "stable" or default_branch == "master":
            self.errors.append("toplevel-unecessary-default-branch")

        cleanup = manifest.get("cleanup")
        if cleanup and "/lib/debug" in cleanup:
            self.errors.append("toplevel-cleanup-debug")

        modules = manifest.get("modules")
        if not modules:
            self.errors.append("toplevel-no-modules")
        else:
            for module in modules:
                for checkclass in checks.ALL:
                    check = checkclass()

                    if check.type == "module":
                        check.check(module)

