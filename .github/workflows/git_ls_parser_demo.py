import git_ls_parser

lines = [
    'i/lf    w/crlf  attr/text eol=crlf    	Rubberduck_Export/App/ufConfirmation.frm',
    'i/lf    w/crlf  attr/text eol=crlf    	"Rubberduck_Export/App/ufEncR\\303\\251gularisation.frm"',
]

parsed_data = git_ls_parser.parse_git_ls_files_output(lines)

# Example access:
print(parsed_data.keys())
print(parsed_data["Rubberduck_Export/App/ufConfirmation.frm"].working_directory) # Shoud print "crlf"
print(parsed_data["Rubberduck_Export/App/ufConfirmation.frm"].attribute_text) # Should print "text"
print(parsed_data["Rubberduck_Export/App/ufConfirmation.frm"].attribute_eol) # Should print "eol=crlf"