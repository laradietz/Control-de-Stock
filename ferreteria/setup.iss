; Inno Setup Script - Ferretería Gian
; Sistema de Control de Stock

#define AppName "Control de Stock - Ferretería Gian"
#define AppVersion "4.0"
#define AppPublisher "Ferretería Gian"
#define AppExeName "ControlStock_Gian.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL=
DefaultDirName={autopf}\ControlStock_Gian
DefaultGroupName={#AppName}
AllowNoIcons=no
OutputDir=INSTALADOR
OutputBaseFilename=Instalar_ControlStock_Gian
SetupIconFile=icono.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
WizardImageFile=
PrivilegesRequired=lowest
DisableProgramGroupPage=no
DisableWelcomePage=no
LicenseFile=
InfoBeforeFile=
InfoAfterFile=
UninstallDisplayIcon={app}\{#AppExeName}
UninstallDisplayName={#AppName}

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el {cm:DesktopName}"; GroupDescription: "Iconos adicionales:"; Flags: checked
Name: "quicklaunchicon"; Description: "Crear acceso directo en Inicio rápido"; GroupDescription: "Iconos adicionales:"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
; Ejecutable principal
Source: "dist\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Base de datos
Source: "db\*"; DestDir: "{app}\db"; Flags: ignoreversion recursesubdirs createallsubdirs

; Carpeta de exports (vacía)
Source: "exports\*"; DestDir: "{app}\exports"; Flags: ignoreversion recursesubdirs createallsubdirs

; Documentación
Source: "docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs createallsubdirs

; Ícono
Source: "icono.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Acceso directo en el Menú Inicio
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\icono.ico"; Comment: "Sistema de control de stock para ferreterías"

; Desinstalar desde el Menú Inicio
Name: "{group}\Desinstalar {#AppName}"; Filename: "{uninstallexe}"

; Acceso directo en el Escritorio
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\icono.ico"; Tasks: desktopicon; Comment: "Sistema de control de stock para ferreterías"

[Run]
; Ejecutar la app al terminar de instalar
Filename: "{app}\{#AppExeName}"; Description: "Abrir Ferretería Gian ahora"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Eliminar carpeta de backups al desinstalar (opcional)
Type: filesandordirs; Name: "{app}\db\backups"

[Messages]
WelcomeLabel2=Este asistente instalará [name/ver] en tu computadora.%n%nSistema de control de stock, ventas, caja, clientes y más.%n%nSe recomienda cerrar todas las demás aplicaciones antes de continuar.
FinishedHeadingLabel=¡Instalación completada!
FinishedLabel=El sistema [name] se instaló correctamente.%n%nHacé clic en "Finalizar" para abrir el programa.%n%nUsuario: dueño%nContraseña: 1234
