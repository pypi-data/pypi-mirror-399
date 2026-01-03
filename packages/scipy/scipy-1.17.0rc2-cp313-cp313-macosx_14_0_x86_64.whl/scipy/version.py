
"""
Module to expose more detailed version info for the installed `scipy`
"""
version = "1.17.0rc2"
full_version = version
short_version = version.split('.dev')[0]
git_revision = "2ff870db068dcf20f9214c2c85bcf4cbbe9cb128"
release = 'dev' not in version and '+' not in version

if not release:
    version = full_version
