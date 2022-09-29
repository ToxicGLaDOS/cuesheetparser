### What it does

This is meant to be used as a library to parse `.cue` files. The main function (and only one that should be called by external code) is `parse` and it returns a dictionary that represents all the data in the cue file. Here's the schema of the dict you get back:

```
{
  'title': str|None,
  'performer': str|None,
  'files': [
    {
      'file_name': str,
      'file_format': 'BINARY'|'MOTOROLA'|'AIFF'|'WAVE'|'MP3'|None,
      'tracks': [
        'track_number': int,
	'title': str|None,
	'performer': str|None,
	'mode': 'AUDIO'|'CDG'|'MODE1/2048'|'MODE1/2352'|'MODE2/2336'|'MODE2/2352'|'CDI/2336'|'CDI/2352',
	'isrc': str|None,
	'flag': 'PRE'|'DCP'|'4CH'|'SCMS'|None
	'indicies': {
          int: str,
	  ...
	},
	'comments': {
          str: str,
	  ...
	}
      ],
      'comments': {
        str: str,
	...
      }
    },
    ...
  ],
  'comments': {
    str: str,
    ...
  }
}
```

There are commands this parser doesn't support yet like PREGAP and POSTGAP. I want to support them, but I can't find an actual .cue file that uses them to test with, so until then, this will have to do!

### How it works

The parser is basically a state machine where each function call is a new state. Each function passes the remaining lines in a list to the next function and the called function always pops at least one line off the front of the list (more if its a function for a section like FILE or TRACK). This method isn't very pythonic, considering we're passing around one list that gets modified by the functions we pass it to, but it seems more readable than the alternative which is to create new lists and return them along with the result.


