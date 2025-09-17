Hi!👋

If you are reading this, it's probably that you got a notification from GitHub Action Bot telling you that there was an issue with you VBA repo.
Hopefully, this README will answer questions you may have regarding what is going on here.

## Motivation

One of the issues with VBA is that there is no commonly accepted method of extracting your VBA project for [version control](https://en.wikipedia.org/wiki/Version_control). This can lead to different approaches that are incompatible with the way Git and GitHub work and cause mislabeled repositories, missing syntax highlighting and other problems. That's where this project comes in: to help fix some of these issues for VBA repositories by suggesting potential fixes.

## How

This repo uses automated scripts via GitHub Actions to check for newly updated VBA repositories and scan for issues. If it finds something, it will create an external issue and mention the owner of the repo to notify them.

## Checks

* Check A: VBA code files are using the Visual Basic .NET file extension.
* Check B: VBA code files are using the VBScript file extension.
* Check C: VBA code files are using no file extension.
* Check D: VBA code files are using the `txt` file extension.
* Check E: VBA repo has a .gitattributes misconfiguration.
* Check F: VBA repo has `.frm` and `.cls` files with un-normalized line endings.

## More info
If you are looking for more info on how to configure your VBA repos, check out [VBA-on-GitHub](https://github.com/DecimalTurn/VBA-on-GitHub). 
