#!/usr/bin/env python
import os
import sys;


sys.path.append(r'/home/raditha/workspace/lampblog/')
sys.path.append('/usr/local/google_appengine/')

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pages.settings")

    if len(sys.argv) > 1:
        command = sys.argv[1]
           
    
    from django.core.management import execute_from_command_line
    
    execute_from_command_line(sys.argv)
