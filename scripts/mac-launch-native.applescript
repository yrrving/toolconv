set scriptPath to "/Users/nicklaskarlsson/Desktop/toolconv/scripts/mac-native-ui.py"
set logPath to "/tmp/BorstbindareWenmanNative.log"

set shellCommand to "export PATH='/Library/Frameworks/Python.framework/Versions/3.13/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin'; " & ¬
	"PYTHON_BIN=''; " & ¬
	"for CANDIDATE in '/Library/Frameworks/Python.framework/Versions/3.13/bin/python3' '/usr/local/bin/python3' '/opt/homebrew/bin/python3'; do " & ¬
	"if [ -x \"$CANDIDATE\" ]; then PYTHON_BIN=\"$CANDIDATE\"; break; fi; " & ¬
	"done; " & ¬
	"if [ -z \"$PYTHON_BIN\" ]; then PYTHON_BIN=$(command -v python3 2>/dev/null || true); fi; " & ¬
	"if [ -z \"$PYTHON_BIN\" ]; then exit 17; fi; " & ¬
	"if [ ! -f " & quoted form of scriptPath & " ]; then exit 18; fi; " & ¬
	"nohup \"$PYTHON_BIN\" " & quoted form of scriptPath & " >" & quoted form of logPath & " 2>&1 &"

try
	do shell script shellCommand
on error errMsg number errNum
	if errNum is 17 then
		display alert "Borstbindare Wenman" message "python3 saknas. Installera python3 och prova igen." as warning
	else if errNum is 18 then
		display alert "Borstbindare Wenman" message "Det native UI-scriptet hittades inte i toolconv-mappen på skrivbordet." as warning
	else
		display alert "Borstbindare Wenman" message errMsg as warning
	end if
end try
