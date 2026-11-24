Unicode True
RequestExecutionLevel user
SetCompressor /SOLID zlib

!include "MUI2.nsh"
!include "x64.nsh"

!define PRODUCT "OKAMI Memórias Escolares"
!define LABEL "${PRODUCT} ${VERSION}"
!define UNINSTALL_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\OkamiMemorias-${VERSION}"

Name "${LABEL}"
OutFile "${SETUP}"
InstallDir "$LOCALAPPDATA\Programs\OKAMI Memorias Escolares\${VERSION}"

!define MUI_ABORTWARNING
!define MUI_FINISHPAGE_RUN "$INSTDIR\OKAMI-Memorias.exe"
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "PortugueseBR"

Function .onInit
  SetShellVarContext current
  ${IfNot} ${RunningX64}
    MessageBox MB_OK|MB_ICONSTOP "Este instalador requer Windows de 64 bits." /SD IDOK
    SetErrorLevel 1
    Quit
  ${EndIf}
  ClearErrors
  ReadRegStr $0 HKCU "${UNINSTALL_KEY}" "UninstallString"
  ${If} $0 != ""
    MessageBox MB_OK|MB_ICONSTOP "Esta versão já está instalada. Abra-a no menu Iniciar." /SD IDOK
    SetErrorLevel 1
    Quit
  ${EndIf}
  IfFileExists "$INSTDIR\*.*" 0 available
    MessageBox MB_OK|MB_ICONSTOP "A pasta de instalação já existe." /SD IDOK
    SetErrorLevel 1
    Quit
  available:
FunctionEnd

Section "Aplicativo"
  ClearErrors
  SetOutPath "$INSTDIR"
  File /r "${BUNDLE}\*"
  IfErrors failed
  WriteUninstaller "$INSTDIR\Desinstalar.exe"
  IfErrors failed
  CreateShortcut "$SMPROGRAMS\${LABEL}.lnk" "$INSTDIR\OKAMI-Memorias.exe"
  IfErrors failed
  WriteRegStr HKCU "${UNINSTALL_KEY}" "DisplayName" "${LABEL}"
  WriteRegStr HKCU "${UNINSTALL_KEY}" "DisplayVersion" "${VERSION}"
  WriteRegStr HKCU "${UNINSTALL_KEY}" "Publisher" "OKAMI Software"
  WriteRegStr HKCU "${UNINSTALL_KEY}" "InstallLocation" "$INSTDIR"
  WriteRegStr HKCU "${UNINSTALL_KEY}" "UninstallString" '"$INSTDIR\Desinstalar.exe"'
  WriteRegDWORD HKCU "${UNINSTALL_KEY}" "NoModify" 1
  WriteRegDWORD HKCU "${UNINSTALL_KEY}" "NoRepair" 1
  IfErrors failed
  Goto done
  failed:
    MessageBox MB_OK|MB_ICONSTOP "Não foi possível concluir a instalação. Verifique as permissões e o espaço em disco." /SD IDOK
    SetErrorLevel 2
    Quit
  done:
SectionEnd

Section "Uninstall"
  SetShellVarContext current
  Delete "$SMPROGRAMS\${LABEL}.lnk"
  DeleteRegKey HKCU "${UNINSTALL_KEY}"
  !include "${FILE_LIST}"
  Delete "$INSTDIR\Desinstalar.exe"
  RMDir "$INSTDIR"
SectionEnd
