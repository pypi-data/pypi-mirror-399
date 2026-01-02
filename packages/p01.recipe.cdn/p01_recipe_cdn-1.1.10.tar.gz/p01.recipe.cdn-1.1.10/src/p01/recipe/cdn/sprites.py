###############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id: sprites.py 5766 2025-12-29 14:12:22Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import os.path
import sys
import traceback


TRUE_VALUES = ['1', 'true', 'True', 'ok', 'yes', True]
FALSE_VALUES = ['0', 'false', 'False', 'no', None, '']


def makeBool(value):
    """Convert a value to boolean."""
    if value in TRUE_VALUES:
        return True
    elif value in FALSE_VALUES:
        return False
    else:
        # raise error if unknown value is given
        raise ValueError("Must use a known bool string, got: %r" % value)


def main(args=None):
    """Main entry point for sprite generation using glue.
    
    This function wraps the external glue package to generate CSS sprites.
    Arguments are passed from the buildout recipe configuration.
    
    Expected positional arguments (from recipe):
        args[0]: source directory
        args[1]: css output directory  
        args[2]: img output directory
        args[3]: url prefix (optional, can be empty string)
        args[4]: project mode ('true'/'false')
        args[5]: less output ('true'/'false')
        args[6]: html output ('true'/'false')
    """
    if args is None:
        args = sys.argv[1:]
    
    # Parse arguments from recipe
    if len(args) < 7:
        print("Error: Not enough arguments provided")
        print("Usage: sprites source css_dir img_dir url project less html")
        sys.exit(1)
    
    source = args[0]
    css_dir = args[1]
    img_dir = args[2]
    url = args[3] if args[3] else None
    project = makeBool(args[4])
    less = makeBool(args[5])
    html = makeBool(args[6])
    
    # Validate source directory
    if not os.path.isdir(source):
        print("Error: Source directory not found: '%s'" % source)
        sys.exit(1)
    
    # Build glue command line arguments
    glue_args = ['glue', source]
    
    # Output directories
    glue_args.extend(['--css', css_dir])
    glue_args.extend(['--img', img_dir])
    
    # Optional URL prefix
    if url:
        glue_args.extend(['--url', url])
    
    # Project mode (multiple sprite folders)
    if project:
        glue_args.append('--project')
    
    # LESS output instead of CSS
    if less:
        glue_args.append('--less')
    
    # Generate HTML test file
    if html:
        glue_args.append('--html')
    
    # Import and run glue
    try:
        from glue.bin import main as glue_main
    except ImportError:
        print("Error: glue package not installed.")
        print("Install it with: pip install glue")
        print("Or use: p01.recipe.cdn[sprites]")
        sys.exit(1)
    
    # Replace sys.argv for glue's argument parser
    old_argv = sys.argv
    try:
        sys.argv = glue_args
        print("Running: %s" % ' '.join(glue_args))
        glue_main()
    except SystemExit as e:
        # glue calls sys.exit(), propagate the exit code
        sys.exit(e.code)
    except Exception:
        traceback.print_exc()
        sys.exit(1)
    finally:
        sys.argv = old_argv
    
    sys.exit(0)


if __name__ == '__main__':
    main()
