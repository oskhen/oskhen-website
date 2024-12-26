# Deploy add

Scope:
	From (obsidian) markdown file into a (new) published entry on oskhen.se

Process:
- Input e.g `deploy add file.md --project "dailies" --section "December 2024"`
- Convert file.md to barebones HTML
- Push HTML file to server
- Add SQL entry
- Update Changelog

Details:
- General
	- Read config from separate file?
- Input
	- section optional?
		- section autofill if empty?
- Conversion
	- Save file locally?
	- Scope of metadata?
	- Strip `<style>` block?
- Deployment
	- Authentication?
		- ssh-key, prompt for password (check if needed?) - defined in config?
- SQL
	- Generate ID
	- Get Current Time
	- Get Filename (title)
	- Parse SQL command properly (quotation issues?) and execute