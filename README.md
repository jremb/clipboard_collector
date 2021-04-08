# clipboard_collector

Inspired by Al Sweigart's multi-clipboard project in Automate the Boring Stuff. Uses pyperclip module to monitor clipboard for content. If content, pastes it into a text field so that similar clippings can easily be grouped together and placed into another repository.

Example use case: Start collecting quotes or highlights from an article. When finished, stop process, copy all of the collected clippings onto the clipboard and paste into a program like OneNote, Evernote, or Zotero. Saves time from switching back and forth from source to, say, Zotero note.

The start button must be engaged before the Append Options are enabled.

For Windows: created an .exe with Pyinstaller and installer with NSIS. Cf. Releases sidebar.

# Known issue:

Copy is sometimes not captured by pyperclip. Ctrl+c keyboard shortcut seems to have more consistent results. Unknown whether this is specific to pyperclip or Windows clipboard. Will look into whether it's possible to use utilize QClipboard.
