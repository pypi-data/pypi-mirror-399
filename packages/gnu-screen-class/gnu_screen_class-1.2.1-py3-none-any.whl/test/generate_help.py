#!/usr/bin/env python3
import io
import sys
import contextlib
import gnuscreen

def capture_help_to_markdown(module):
    # Create a string IO stream to capture the output
    with io.StringIO() as buf, contextlib.redirect_stdout(buf):
        # Call help on the module
        help(module)
        # Get the output from the buffer
        output = buf.getvalue()
    
    # Format the output as Markdown
    markdown_output = "```plaintext\n" + output + "\n```"
    return markdown_output

markdown_help = capture_help_to_markdown(gnuscreen)

# Print or save the Markdown output
print(markdown_help)

