def convert_to_html(text):
    # Start with an HTML template that includes the <pre> tag to preserve formatting
    html_content = f"""<html>
<head></head>
<body>
<pre>
{text}
</pre>
</body>
</html>"""
    
    return html_content


# Example input (raw text, exactly as you want it)
text = """
MPC#:	S01022	Sequence:	#1239	(22-06)
Spud Date: 4/7/2022
Program: 2021 Sumner County Exploration & Development Program
Prospect: Jack Daniels
Contractor: Lighthouse Drilling, LLC
Wellsite Geologist: Dave Williams (C: 316-303-4932)
Contact Geologist: Evan Stone (C: 913-972-2577)
                Depth	 Datum	Position
Heebner	        2192	-947	+27
Iatan	        2488	-1243	+28
Stalnaker Sand	2563	-1318	+8
"""

# Convert to HTML
html_content = convert_to_html(text)

# Save to a file
with open("generated_content.html", "w") as file:
    file.write(html_content)

print("HTML content generated and saved.")
