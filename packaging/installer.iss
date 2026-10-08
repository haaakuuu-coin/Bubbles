; Inno Setup (open source): genera "TTS Chatbot Setup.exe" a partir de dist\TTSChatbot
; NO PROBADO en esta entrega. El modelo (~337 MB) se descarga desde la app, no se incluye.
[Setup]
AppName=TTS Chatbot
AppVersion=0.1.0
DefaultDirName={autopf}\TTS Chatbot
DefaultGroupName=TTS Chatbot
OutputBaseFilename=TTS Chatbot Setup
Compression=lzma2
[Files]
Source: "..\dist\TTSChatbot\*"; DestDir: "{app}"; Flags: recursesubdirs
[Icons]
Name: "{group}\TTS Chatbot"; Filename: "{app}\TTSChatbot.exe"
Name: "{autodesktop}\TTS Chatbot"; Filename: "{app}\TTSChatbot.exe"
[Run]
Filename: "{app}\TTSChatbot.exe"; Description: "Abrir TTS Chatbot"; Flags: postinstall nowait
