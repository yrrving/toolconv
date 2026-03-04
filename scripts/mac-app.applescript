set ffmpegPath to "/opt/homebrew/bin/ffmpeg"

try
  set inputFile to choose file with prompt "Välj en MP4-fil att konvertera till WAV:" of type {"public.mpeg-4"}
on error number -128
  return
end try

set inputPosix to POSIX path of inputFile

tell application "System Events"
  set originalName to name of inputFile
end tell

if originalName ends with ".mp4" then
  set baseName to text 1 thru -5 of originalName
else
  set AppleScript's text item delimiters to "."
  set nameParts to text items of originalName
  if (count of nameParts) > 1 then
    set baseName to (items 1 thru -2 of nameParts) as text
  else
    set baseName to originalName
  end if
  set AppleScript's text item delimiters to ""
end if

try
  set outputFile to choose file name with prompt "Spara WAV-filen som:" default name (baseName & ".wav")
on error number -128
  return
end try

set outputPosix to POSIX path of outputFile

try
  do shell script quoted form of ffmpegPath & " -y -i " & quoted form of inputPosix & " -vn -acodec pcm_s16le " & quoted form of outputPosix
  display dialog "Konverteringen är klar." buttons {"OK"} default button "OK"
on error errMsg
  display alert "Konverteringen misslyckades" message errMsg as warning
end try
